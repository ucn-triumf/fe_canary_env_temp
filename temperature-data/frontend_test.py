# listens for messages from canaries, does something with them when they arrive
# paho code from https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#usage-and-api

import paho.mqtt.client as mqtt
import json

import midas
import midas.frontend
import midas.event


broker_address = "127.0.0.1"
broker_port = 8883

temperature = 1.0
humidity = 1.0
currentMAC = 'abcdefghijkl'


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # Subscribe to all canaries:
    client.subscribe([("msr/84CCA8842F45", 1), ("msr/E8DB8496A0F6", 1), ("msr/9C9C1F458F3A", 1), ("msr/9C9C1F45B1E3", 1)])


# the callback for when a PUBLISH message is received from server
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    global temperature
    global humidity
    global currentMAC
    json_data = json.loads(msg.payload)
    temp = json_data['temperature']
    hum = json_data['relativehumidity']
    currentMAC = (msg.topic).split('/')[1]
    print(currentMAC)
    if isinstance(temp, float) and isinstance(hum, float):
        temperature = temp
        humidity = hum
    else:
        temperature = 0.0
        humidity = 0.0
    print(temperature, humidity)





class MyPeriodicEquipment(midas.frontend.EquipmentBase):
    """
    We define an "equipment" for each logically distinct task that this frontend
    performs. For example, you may have one equipment for reading data from a
    device and sending it to a midas buffer, and another equipment that updates
    summary statistics every 10s.
    
    Each equipment class you define should inherit from 
    `midas.frontend.EquipmentBase`, and should define a `readout_func` function.
    If you're creating a "polled" equipment (rather than a periodic one), you
    should also define a `poll_func` function in addition to `readout_func`.
    """
    def __init__(self, client):
        # The name of our equipment. This name will be used on the midas status
        # page, and our info will appear in /Equipment/MyPeriodicEquipment in
        # the ODB.
        equip_name = "EnvTempReadout"
        
        # Define the "common" settings of a frontend. These will appear in
        # /Equipment/MyPeriodicEquipment/Common. The values you set here are
        # only used the very first time this frontend/equipment runs; after 
        # that the ODB settings are used.
        default_common = midas.frontend.InitialEquipmentCommon()
        default_common.equip_type = midas.EQ_PERIODIC
        default_common.buffer_name = "SYSTEM"
        default_common.trigger_mask = 0
        default_common.event_id = 1
        default_common.period_ms = 100
        default_common.read_when = midas.RO_ALWAYS
        default_common.log_history = 1
        
        # You MUST call midas.frontend.EquipmentBase.__init__ in your equipment's __init__ method!
        midas.frontend.EquipmentBase.__init__(self, client, equip_name, default_common)
        
        # You can set the status of the equipment (appears in the midas status page)
        self.set_status("Initialized")
        
    def readout_func(self):
        """
        For a periodic equipment, this function will be called periodically
        (every 100ms in this case). It should return either a `cdms.event.Event`
        or None (if we shouldn't write an event).
        """
        
        # In this example, we just make a simple event with one bank.
        event = midas.event.Event()
        
        # Create a bank (called "MYBK") which in this case will store 8 ints.
        # data can be a list, a tuple or a numpy array.
        
        data = [temperature,humidity,7]
        if(currentMAC == '84CCA8842F45'):
            event.create_bank("CNY1", midas.TID_FLOAT, data)
        elif(currentMAC == 'E8DB8496A0F6'):
            event.create_bank("CNY2", midas.TID_FLOAT, data)

        return event

class MyFrontend(midas.frontend.FrontendBase):
    """
    A frontend contains a collection of equipment.
    You can access self.client to access the ODB etc (see `midas.client.MidasClient`).
    """
    def __init__(self):
        # You must call __init__ from the base class.
        midas.frontend.FrontendBase.__init__(self, "fe_envtemp")
        
        # You can add equipment at any time before you call `run()`, but doing
        # it in __init__() seems logical.
        self.add_equipment(MyPeriodicEquipment(self.client))
        
    def begin_of_run(self, run_number):
        """
        This function will be called at the beginning of the run.
        You don't have to define it, but you probably should.
        You can access individual equipment classes through the `self.equipment`
        dict if needed.
        """
        self.set_all_equipment_status("Running", "greenLight")
        self.client.msg("Frontend has seen start of run number %d" % run_number)
        return midas.status_codes["SUCCESS"]
        
    def end_of_run(self, run_number):
        self.set_all_equipment_status("Finished", "greenLight")
        self.client.msg("Frontend has seen end of run number %d" % run_number)
        return midas.status_codes["SUCCESS"]
        
if __name__ == "__main__":

    client = mqtt.Client("P1")  # P1 is a unique identifier
    client.on_connect = on_connect  # smarter: could put on_connect stuff into readout_func and then just make readout_func the client.on_connect
    # wait no, that wouldn't work bc readout_func is called continuously and it's (self)
    client.on_message = on_message
    
    client.username_pw_set("canary", "measuretemp")
    client.connect(broker_address, broker_port)

    client.loop_start()

    # The main executable is very simple - just create the frontend object,
    # and call run() on it.
    my_fe = MyFrontend()
    my_fe.run()

    client.loop_stop()








