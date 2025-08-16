class PaymentIntent:
    def __init__(self,merchants,payment_intents,states):
        self.merchants=merchants
        self.payment_intents=payment_intents
        self.states=states
    def init(self,merchant_id,starting_balance):
        for i in self.merchants:
            if(i[0]==merchant_id):
                pass
        self.merchants.append([merchant_id,starting_balance])
    def create(self,payment_intent_id,merchant_id,amount):
        self.payment_intents.append([payment_intent_id,merchant_id,amount,self.states[0]])
    def attempt(self,payment_intent_id):
        for i in range(0,len(self.payment_intents)):
            if(self.payment_intents[i][0]==payment_intent_id):
                self.payment_intents[i][3]=self.states[1]
                for j in range(0,len(self.merchants)):
                    if (self.merchants[j][0]==self.payment_intents[i][1]):
                        self.merchants[j][1]+=self.payment_intents[i][2]
    def succeed(self,payment_intent_id):
        for i in range(0,len(self.payment_intents)):
            if(self.payment_intents[i][0]==payment_intent_id):
                self.payment_intents[i][3]=self.states[2]
    def update(self,payment_intent_id,new_amount):
        for i in range(0,len(self.payment_intents)):
            if(self.payment_intents[i][0]==payment_intent_id):
                self.payment_intents[i][2]=new_amount
    def fail(self,payment_intent_id):
        for i in range(0,len(self.payment_intents)):
            if(self.payment_intents[i][0]==payment_intent_id):
                self.payment_intents[i][3]=self.states[0]
    def refund(self,payment_intent_id):
        for i in range(0,len(self.payment_intents)):
            if(self.payment_intents[i][0]==payment_intent_id):
                self.payment_intents[i][3]=self.states[0]
                for j in range(0,len(self.merchants)):
                    if (self.merchants[j][0]==self.payment_intents[i][1]):
                        self.merchants[j][1]-=self.payment_intents[i][2]
                
def main():
    payment_intents=[]
    merchants=[]
    commands_preproc=[]
    states=["REQUIRES_ACTION","PROCESSING","COMPLETED"]
    obj=PaymentIntent(merchants,payment_intents,states)
    while True:
        hello=(input("Enter the commands: ").strip())
        print(f"--{hello}--")
        if hello=="\n" or hello=="" or hello=="DONE":
            break
        else:
            commands_preproc.append(hello)
    for i in commands_preproc:
        j=i.split()
        if(j[0]=="INIT"):
            obj.init(j[1],int(j[2]))
        elif(j[0]=="CREATE"):
            obj.create(j[1],j[2],int(j[3]))
        elif(j[0]=="ATTEMPT"):
            obj.attempt(j[1])
        elif(j[0]=="SUCCEED"):
            obj.succeed(j[1])
        elif(j[0]=="UPDATE"):
            obj.update(j[1],int(j[2]))
        elif(j[0]=="FAIL"):
            obj.fail(j[1])
        elif(j[0]=="REFUND"):
            obj.refund(j[1])
        else:
            print(f"INVALID COMMAND {j}")
    obj.merchants.sort()
    print(obj.merchants)
    print(obj.payment_intents)
if __name__=="__main__":
    main()