from __future__ import annotations
import importlib.util, json, time, uuid
from typing import Any

def _version(package:str)->str:
    try:
        from importlib.metadata import version
        return version(package)
    except Exception: return ''

def dependency_status()->dict[str,Any]:
    mi=importlib.util.find_spec('meshtastic') is not None; ps=importlib.util.find_spec('serial') is not None; pub=importlib.util.find_spec('pubsub') is not None
    return {'meshtastic_installed':mi,'meshtastic_version':_version('meshtastic') if mi else '','pyserial_installed':ps,'pyserial_version':_version('pyserial') if ps else '','pubsub_installed':pub,'state':'dependency_ready' if mi and ps else 'missing_dependency'}

def list_candidate_ports()->list[dict[str,str]]:
    try:
        from serial.tools import list_ports
        return [{'device':p.device,'description':p.description,'hwid':p.hwid} for p in list_ports.comports()]
    except Exception as exc: return [{'device':'','description':'pyserial list_ports unavailable','hwid':str(exc)}]

def record_event(store,event_type:str,details:dict[str,Any],state:str)->None:
    with store.connect() as conn: conn.execute('INSERT INTO meshtastic_events(event_id,event_type,state,details_json) VALUES (?,?,?,?)',('mesh_'+uuid.uuid4().hex[:12],event_type,state,json.dumps(details,sort_keys=True))); conn.commit()

def latest_status(store)->dict[str,Any]:
    try:
        with store.connect() as conn: row=conn.execute('SELECT * FROM meshtastic_events ORDER BY created_at DESC LIMIT 1').fetchone()
        if not row: return {'state':'not_tested','last_event':'','last_error':'','nodes_seen':0}
        d=dict(row)
        try: details=json.loads(d.get('details_json') or '{}')
        except Exception: details={}
        return {'state':d.get('state') or 'not_tested','last_event':d.get('event_type') or '','last_error':details.get('error',''),'nodes_seen':details.get('nodes_seen',0),'last_checked':d.get('created_at','')}
    except Exception: return {'state':'not_tested','last_event':'','last_error':'','nodes_seen':0}

def probe_serial(store,port:str='',timeout_s:float=8.0)->dict[str,Any]:
    deps=dependency_status()
    if not deps.get('meshtastic_installed'):
        result={**deps,'ok':False,'state':'missing_dependency','error':'meshtastic package is not installed'}; record_event(store,'probe_serial',result,'missing_dependency'); return result
    try:
        import meshtastic.serial_interface  # type: ignore
        start=time.time(); iface=meshtastic.serial_interface.SerialInterface(devPath=port or None); elapsed=int((time.time()-start)*1000)
        nodes=getattr(iface,'nodes',None) or {}; my_info=getattr(iface,'myInfo',None); metadata=getattr(iface,'metadata',None)
        try: iface.close()
        except Exception: pass
        result={**deps,'ok':True,'state':'connected','port':port or 'auto','elapsed_ms':elapsed,'nodes_seen':len(nodes) if hasattr(nodes,'__len__') else 0,'myInfo':str(my_info)[:500],'metadata':str(metadata)[:500]}; record_event(store,'probe_serial',result,'connected'); return result
    except Exception as exc:
        result={**deps,'ok':False,'state':'probe_failed','port':port or 'auto','error':str(exc)[:1000]}; record_event(store,'probe_serial',result,'probe_failed'); return result

def send_text(store,text:str,port:str='',destination_id:str='^all')->dict[str,Any]:
    deps=dependency_status(); text=(text or 'CMN1|PING|body=hello from CommNet')[:180]
    if not deps.get('meshtastic_installed'):
        result={**deps,'ok':False,'state':'missing_dependency','error':'meshtastic package is not installed'}; record_event(store,'send_text',result,'missing_dependency'); return result
    try:
        import meshtastic.serial_interface  # type: ignore
        iface=meshtastic.serial_interface.SerialInterface(devPath=port or None); iface.sendText(text,destinationId=destination_id or '^all')
        try: iface.close()
        except Exception: pass
        result={**deps,'ok':True,'state':'sent','port':port or 'auto','text_preview':text,'destination_id':destination_id}; record_event(store,'send_text',result,'sent'); return result
    except Exception as exc:
        result={**deps,'ok':False,'state':'send_failed','port':port or 'auto','error':str(exc)[:1000]}; record_event(store,'send_text',result,'send_failed'); return result
