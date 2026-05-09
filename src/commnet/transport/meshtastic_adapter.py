from __future__ import annotations
from commnet.hardware.meshtastic_probe import dependency_status, probe_serial, send_text
class MeshtasticSerialAdapter:
    adapter_id='meshtastic_serial'
    def __init__(self,store,port:str=''): self.store=store; self.port=port
    def status(self): return dependency_status()
    def probe(self): return probe_serial(self.store,self.port)
    def send_text(self,text:str,destination_id:str='^all'): return send_text(self.store,text,self.port,destination_id)
class FakeMeshtasticAdapter:
    adapter_id='meshtastic_fake'
    def __init__(self,store=None): self.store=store
    def status(self): return {'state':'simulated','meshtastic_installed':False,'ok':True}
    def probe(self): return {'state':'simulated','ok':True,'nodes_seen':2,'note':'fake Meshtastic smoke adapter'}
    def send_text(self,text:str,destination_id:str='^all'): return {'state':'simulated_sent','ok':True,'text_preview':(text or '')[:180],'destination_id':destination_id}
