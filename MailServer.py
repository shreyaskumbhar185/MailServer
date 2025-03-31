import mysql.connector as mysql
import sys
from tkinter import *
from tkinter import messagebox
from datetime import datetime

mycon = mysql.connect(host="localhost",user="root",passwd="shreyas",database="mailserver")
#mycon=sql.connect(host="localhost",user="root",passwd="podar",database="mailserver")


#mysql
'''
create database mailserver
use databasemailserver
create table login(user char(69), passw char(69),date date,nn varchar(50));
select * from login;
'''

#mail software

def newlogininterface():
   global user_id
   global pass_id
   global con_id
   global nickname
   dnt()
   
   root=Tk()
   root.title('New Login')
   root.geometry('340x440')
   root.configure(bg="#333333")

   a1=Label(root,text='Sign Up',bg="#333333",fg="white",font=("Algerian",30,"bold"))
   a1.place(x=100,y=10)

   a2=Label(root,text='username',bg="#333333",fg="white",font=("ariel"))
   a2.place(x=0,y=100)
   user_id=Entry(root,width=28,border=0,fg='white',bg='grey',font=("ariel"))
   user_id.place(x=80,y=100)

   a3=Label(root,text='password',bg="#333333",fg="white",font=("ariel"))
   a3.place(x=0,y=150)
   pass_id=Entry(root,width=28,border=0,fg='white',bg='grey',font=("ariel"))
   pass_id.place(x=80,y=150)

   a4=Label(root,text='confirm',bg="#333333",fg="white",font=("ariel"))
   a4.place(x=0,y=200)
   con_id=Entry(root,width=28,border=0,fg='white',bg='grey',font=("ariel"))
   con_id.place(x=80,y=200)

   a5=Label(root,text='Nickname',bg="#333333",fg="white",font=("ariel"))
   a5.place(x=0,y=250)
   nickname=Entry(root,width=28,border=0,fg='white',bg='grey',font=("ariel"))
   nickname.place(x=80,y=250)
   
   Button(root,width=20,text='Sign Up',bg='white',border=1,font=("ariel black",10,"bold"),command=newlog).place(x=90,y=300)

def newlog():                                                                                                                                           
    user=user_id.get()
    passw=pass_id.get()
    conpassw=con_id.get()
    nn=nickname.get()
    cursor=mycon.cursor()
    cursor.execute("select user from login")
    a=cursor.fetchall()

    if (user,) in a:# if username is not in a direct next loop
        messagebox.showwarning("","Username Already Taken")
        newlogininterface()

    if passw==conpassw:
        
        cursor=mycon.cursor()
        cursor.execute("insert into login values(%s,%s,%s,%s)",(user,passw,now,nn))
        cursor.execute("create table " +user+" (sent int ,recieved int)")
        cursor.execute("insert into " +user+" values(0,0)")
        mycon.commit()
        messagebox.showinfo("","your account has been created please login ")
        logininterface()
    else:
        messagebox.showwarning("","Password doesnt match! Try Again")
        newlogininterface()

def log():
        global user
        user=user_id.get()
        passw=pass_id.get()
        cursor=mycon.cursor()
        cursor.execute("select passw from login where user=%s", [user])        
        data=cursor.fetchall()
        if (passw,) in data:
            f=open(user,"a+")
            messagebox.showinfo("","Login Completed ")
            home()
        elif (passw=="svs" )and (user=="admin"):
            messagebox.showinfo("","Login Completed ")
            main()

        else:
            messagebox.showwarning("","Username or Password doesnt match! Try Again")
            logininterface()

def createopt():
   global messg
   def create():
      usernamelist=user_id.get().split(",")
      messg=body.get("1.0",'end')
      b=open(user,"a+")
      b.write("me"+":-" + messg)
      b.write("%s"%now)
      b.write("\n")
      cursor=mycon.cursor()
      cursor.execute("update " +user+" set sent=sent+1",)
      mycon.commit()
    
      cursor=mycon.cursor()
      cursor.execute("select user from login")
      a=cursor.fetchall()
      
      for username in usernamelist:
         if (username,) in a:
             c=open(username,"a+")
             c.write(user + ":-" + messg)
             c.write("%s"%now)
             c.write("\n")
             messagebox.showinfo("","Message sent")
             cursor=mycon.cursor()
             cursor.execute("update " +username+" set recieved=recieved+1")
             mycon.commit()
             home()
       
         else:
             messagebox.showwarning("","Usernames doesnt exist! Try Again")
             createopt()

   root=Tk()
   root.title('New message')
   root.geometry('800x500')
   root.configure(bg="#333333")

   username=Label(root,text='To:-',bg="#333333",fg="white",font=("ariel"))
   username.place(x=50,y=50)
   user_id=Entry(root,width=70,fg='white',bg='grey',font=("ariel"))
   user_id.place(x=100,y=50)

   body=Text(root,width=80,height=10,fg='white',bg='grey',font=("ariel"))
   body.place(x=50,y=100)

   Button(root,width=20,text='Send',bg='grey',fg='white',border=1,font=("ariel black",10,"bold"),command=create).place(x=50,y=350)
   
   root.mainloop

def logininterface():
   global user_id
   global pass_id
   global con_id 
   
   root=Tk()
   root.title('Login')
   root.geometry('340x440')
   root.configure(bg="#333333")

   a1=Label(root,text='LOGIN',bg="#333333",fg="white",font=("Algerian",30,"bold"))
   a1.place(x=115,y=10)

   a2=Label(root,text='username',bg="#333333",fg="white",font=("ariel"))
   a2.place(x=0,y=100)
   user_id=Entry(root,width=28,border=0,fg='white',bg='grey',font=("ariel"))
   user_id.place(x=80,y=100)

   a3=Label(root,text='password',bg="#333333",fg="white",font=("ariel"))
   a3.place(x=0,y=150)
   pass_id=Entry(root,width=28,border=0,fg='white',bg='grey',font=("ariel"),show="*")
   pass_id.place(x=80,y=150)
   
   Button(root,width=12,text='show password',bg='#333333',fg="white",border=0,font=("ariel black",10,"bold"),command=show).place(x=230,y=170)
   Button(root,width=20,text='Submit',bg='white',border=1,font=("ariel black",10,"bold"),command=log).place(x=90,y=200)
   Button(root,width=0,text='Forgot password?',bg='#333333',fg='light blue',border=0,font=("Cascadia Code",15,"underline"),command=fpassinterface).place(x=0,y=250)
   
   a4=Label(root,text='Do not have an account?',bg="#333333",fg="white",font=("Cascadia Code",15,"underline"))
   a4.place(x=0,y=340)

   Button(root,width=0,text='Click to Sign Up!',bg='#333333',fg='light blue',border=0,font=("Cascadia Code",15,"underline"),command=newlogininterface).place(x=0,y=370)
   root.mainloop

def show():
   if pass_id.cget('show')=="*":
      pass_id.config(show='')
       
   else:
      pass_id.config(show='*')

def readinterface():
   
   b=open(user,"r+")
   c=b.read()
   
   root=Tk()
   root.title('Inbox')
   root.geometry('800x500')
   root.configure(bg="#333333")

   a1=Label(root,text='Your Inbox ',bg="#333333",fg="white",font=("Algerian",30,"bold"))
   a1.place(x=250,y=10)

   a2=Label(root,text=c,bg="#333333",fg="white",font=("Times New Roman",14,"bold"))
   a2.place(x=0,y=50)

   Button(root,width=0,text='back',bg="#201328",fg="white",border=1,font=("ariel black",10,"bold"),command=home).place(x=750,y=0)
   Button(root,width=0,text='reply',bg="#201328",fg="white",border=1,font=("ariel black",10,"bold"),command=createopt).place(x=750,y=30)
   Button(root,width=0,text='forward',bg="#201328",fg="white",border=1,font=("ariel black",10,"bold"),command=forward).place(x=750,y=60)

def forward():
   
   def forwardbutton():
      B=open(user,"r+")
      C=B.read()
     
      usernamelist=(user_id.get()).split(",")
      b=open(user,"a+")
      b.write("me"+":-" +C)
      b.write("%s"%now)
      b.write("\n")
      
      cursor=mycon.cursor()
      cursor.execute("select user from login")
      a=cursor.fetchall()
      for username in usernamelist:
         if (username,) in a:
             c=open(username,"a+")
             c.write(user+":-"+C)
             c.write("%s"%now)
             c.write("\n")
             messagebox.showinfo("","Message sent")
             home()
       
         else:
             messagebox.showwarning("","Usernames doesnt exist! Try Again")
   root=Tk()
   root.title('New message')
   root.geometry('800x500')
   root.configure(bg="#333333")

   username=Label(root,text='To:-',bg="#333333",fg="white",font=("ariel"))
   username.place(x=50,y=50)
   user_id=Entry(root,width=70,fg='white',bg='grey',font=("ariel"))
   user_id.place(x=100,y=50)

   Button(root,width=20,text='Send',bg='grey',fg='white',border=1,font=("ariel black",10,"bold"),command=forwardbutton).place(x=50,y=350)
   Button(root,width=0,text='back',bg="#201328",fg="white",border=1,font=("ariel black",10,"bold"),command=home).place(x=750,y=0)

   root.mainloop
   
def home():
   
   root=Tk()
   root.title('Home')
   root.geometry('800x700')
   root.configure(bg="#333333")

   a1=Label(root,text='Home',bg="#333333",fg="white",font=("Algerian",30,"bold"))
   a1.place(x=280,y=10)

   a2=Label(root,text="Welcome to IFC messenger!!",bg="#333333",fg="white",font=("Times New Roman",14,"bold"))
   a2.place(x=0,y=70)

   Button(root,width=0,text='1.Create Mail',bg="#333333",fg="white",border=1,font=("Algerian",10,"bold"),command=createopt).place(x=10,y=120)
   Button(root,width=0,text='2.Your Inbox',bg="#333333",fg="white",border=1,font=("Algerian",10,"bold"),command=readinterface).place(x=10,y=170)
   Button(root,width=0,text='3.Give feedback',bg="#333333",fg="white",border=1,font=("Algerian",10,"bold"),command=givefb).place(x=10,y=220)
   Button(root,width=0,text='4.logout',bg="#333333",fg="white",border=1,font=("Algerian",10,"bold"),command=logout).place(x=10,y=270)
   Button(root,width=0,text='5.Delete Account',bg="#333333",fg="white",border=1,font=("Algerian",10,"bold"),command=deleteacc).place(x=10,y=320)
   Button(root,width=0,text='6.Change Password',bg="#333333",fg="white",border=1,font=("Algerian",10,"bold"),command=cpassinterface).place(x=10,y=370)
   Button(root,width=0,text='7.About server',bg="#333333",fg="white",border=1,font=("Algerian",10,"bold"),command=about).place(x=10,y=420)
   root.mainloop()
 
def main():
   
   root=Tk()
   root.title('Main')
   root.geometry('800x500')
   root.configure(bg="#333333")

   a1=Label(root,text='OWNER ACCESS HOME PAGE',bg="#333333",fg="white",font=("Algerian",30,"bold"))
   a1.place(x=160,y=10)

   a2=Label(root,text="Welcome to IFC Owner access!!",bg="#333333",fg="white",font=("Times New Roman",14,"bold"))
   a2.place(x=0,y=70)

   Button(root,width=0,text='1.Accounts',bg="#333333",fg="white",border=1,font=("Algerian",10,"bold"),command=displayacc).place(x=10,y=120)
   Button(root,width=0,text='2.Broadcast',bg="#333333",fg="white",border=1,font=("Algerian",10,"bold"),command=broadcast).place(x=10,y=170)
   Button(root,width=0,text='3.Statistics',bg="#333333",fg="white",border=1,font=("Algerian",10,"bold"),command=reportgen).place(x=10,y=220)
   Button(root,width=0,text='4.Feedback responses',bg="#333333",fg="white",border=1,font=("Algerian",10,"bold"),command=fr).place(x=10,y=270)
   Button(root,width=0,text='5.About us',bg="#333333",fg="white",border=1,font=("Algerian",10,"bold"),command=about).place(x=10,y=320)

   root.mainloop()


def logout():
    messagebox.showinfo("","logged out succesfully")
    logininterface()

def cpassinterface():
   global user
   global newpassw_id
   global nn_id
   dnt()
   
   root=Tk()
   root.title('New Login')
   root.geometry('340x440')
   root.configure(bg="#333333")

   a1=Label(root,text='Change',bg="#333333",fg="white",font=("Algerian",30,"bold"))
   a1.place(x=100,y=10)

   a3=Label(root,text='new pass',bg="#333333",fg="white",font=("ariel"))
   a3.place(x=0,y=150)
   newpassw_id=Entry(root,width=28,border=0,fg='white',bg='grey',font=("ariel"))
   newpassw_id.place(x=80,y=150)

   a4=Label(root,text='Nickname',bg="#333333",fg="white",font=("ariel"))
   a4.place(x=0,y=200)
   nn_id=Entry(root,width=28,border=0,fg='white',bg='grey',font=("ariel"))
   nn_id.place(x=80,y=200)

   Button(root,width=20,text='Change',bg='white',border=1,font=("ariel black",10,"bold"),command=cpass).place(x=90,y=300)

def cpass():
       newpasswf=newpassw_id.get()
       nnf=nn_id.get()
       cursor=mycon.cursor()
       cursor.execute("select nn from login where user="+"'"+ user+"'")
       b=cursor.fetchone()
       if nnf==b[0]:
           cursor=mycon.cursor()
           cursor.execute("update login set passw="+"'"+ newpasswf+"'" +" where user="+"'"+ user+"'")
           mycon.commit()
           messagebox.showinfo("","your password has been changed please login ")
           logininterface()
       else:
           messagebox.showwarning("","Nickname doesnt match!")
           cpassinterface()
   

def deleteacc():
    cursor=mycon.cursor()
    cursor.execute("delete from login where user="+"'"+ user+"'")
    cursor.execute("drop table "+user)
    mycon.commit()
    messagebox.showinfo("","Your account has been deleted!")
    
def displayacc():
    
    from tkinter import ttk
    root=Tk()
    root.title('Accounts')
    root.geometry('1350x750')
    root.configure(bg="#333333")
    Button(root,width=0,text='back',bg="#201328",fg="white",border=1,font=("ariel black",10,"bold"),command=main).place(x=1069,y=0)

    s = ttk.Style()
    s.theme_use('clam')

    tree = ttk.Treeview(root, column=("c1", "c2", "c3","c4"), show='headings', height=5)

    tree.column("# 1", anchor=CENTER)
    tree.heading("# 1", text="Username")
    tree.column("# 2", anchor=CENTER)
    tree.heading("# 2", text="Password")
    tree.column("# 3", anchor=CENTER)
    tree.heading("# 3", text="Date")
    tree.column("# 4", anchor=CENTER)
    tree.heading("# 4", text="Nickname")

    a1=Label(root,text='Accounts',bg="#333333",fg="white",font=("Algerian",30,"bold"))
    a1.place(x=10,y=10)
    cursor.execute("select * from login")
    acc=cursor.fetchall()
    for i in range(0,len(acc),1):
        tree.insert('', 'end', text="i", values=acc[i])
        
    tree.place(x=20,y=100)

def fr():
   b=open("admin.txt","r+")
   c=b.read()
   root=Tk()
   root.title('Inbox')
   root.geometry('800x500')
   root.configure(bg="#333333")

   a1=Label(root,text='Feedback Responses ',bg="#333333",fg="white",font=("Algerian",30,"bold"))
   a1.place(x=0,y=10)

   a2=Label(root,text=c,bg="#333333",fg="white",font=("Times New Roman",14,"bold"))
   a2.place(x=0,y=50)

   Button(root,width=0,text='back',bg="#201328",fg="white",border=1,font=("ariel black",10,"bold"),command=home).place(x=1000,y=0)
   
def givefb():
   def fb():
      messg=body.get("1.0",'end')
      c=open("admin.txt","a+")
      c.write(user+":-" + messg)
      c.write("\n")
      messagebox.showinfo("","feedback submitted!")
      home()
     
   root=Tk()
   root.title('New message')
   root.geometry('800x500')
   root.configure(bg="#333333")

   body=Text(root,width=80,height=10,fg='white',bg='grey',font=("ariel"))
   body.place(x=50,y=100)

   Button(root,width=20,text='Submit',bg='grey',fg='white',border=1,font=("ariel black",10,"bold"),command=fb).place(x=50,y=350)
   Button(root,width=0,text='back',bg="#201328",fg="white",border=1,font=("ariel black",10,"bold"),command=home).place(x=750,y=0)

     
def dnt():
   global now
   now = datetime.now()

def broadcast():

   root=Tk()
   root.title('New message')
   root.geometry('800x500')
   root.configure(bg="#333333")
   body=Text(root,width=80,height=10,fg='white',bg='grey',font=("ariel"))
   body.place(x=50,y=100)
   messg=body.get("1.0",'end')

   def brcst():

       messg=body.get("1.0",'end')
       for username in allu:
         
          b=open(username[0],"a+")
          b.write(user+":-"+messg)
          b.write("%s"%now)
          b.write("\n")

       messagebox.showinfo("","Message sent")
          
   Button(root,width=20,text='Send',bg='grey',fg='white',border=1,font=("ariel black",10,"bold"),command=brcst).place(x=50,y=350)
   Button(root,width=0,text='back',bg="#201328",fg="white",border=1,font=("ariel black",10,"bold"),command=main).place(x=750,y=0)
   root.mainloop


def fpass():
       userf=user_id.get()
       newpasswf=newpassw_id.get()
       nnf=nn_id.get()
       cursor=mycon.cursor()
       cursor.execute("select nn from login where user="+"'"+ userf+"'")
       b=cursor.fetchone()
       if nnf==b[0]:
           cursor=mycon.cursor()
           cursor.execute("update login set passw="+"'"+ newpasswf+"'" +" where user="+"'"+ userf+"'")
           mycon.commit()
           messagebox.showinfo("","your password has been changed please login ")
           logininterface()
       else:
           messagebox.showwarning("","Nickname doesnt match!")
           fpassinterface()

def fpassinterface():
   global user_id
   global newpassw_id
   global nn_id
   dnt()
   
   root=Tk()
   root.title('New Login')
   root.geometry('340x440')
   root.configure(bg="#333333")

   a1=Label(root,text='Forgot',bg="#333333",fg="white",font=("Algerian",30,"bold"))
   a1.place(x=100,y=10)

   a2=Label(root,text='username',bg="#333333",fg="white",font=("ariel"))
   a2.place(x=0,y=100)
   user_id=Entry(root,width=28,border=0,fg='white',bg='grey',font=("ariel"))
   user_id.place(x=80,y=100)

   a3=Label(root,text='new pass',bg="#333333",fg="white",font=("ariel"))
   a3.place(x=0,y=150)
   newpassw_id=Entry(root,width=28,border=0,fg='white',bg='grey',font=("ariel"))
   newpassw_id.place(x=80,y=150)

   a4=Label(root,text='Nickname',bg="#333333",fg="white",font=("ariel"))
   a4.place(x=0,y=200)
   nn_id=Entry(root,width=28,border=0,fg='white',bg='grey',font=("ariel"))
   nn_id.place(x=80,y=200)

   Button(root,width=20,text='Sign Up',bg='white',border=1,font=("ariel black",10,"bold"),command=fpass).place(x=90,y=300)


def about():
   window = Tk()
   window.title("About")
   window.config(bg="#103857")
   window.geometry('1350x750')

   a1=Label(window,text='ABOUT US',bg="#103857",fg="white",font=("Algerian",30,"bold","underline")).place(x=500,y=0)
   about=("This sever is made by team IFC1.The following group members:-")
   about1="i)Sahil Malawde- Front end developer and GUI incharge."
   about2="ii)Shreyas Kumbhar-Database analyst and testing incharge."
   about3="iii)Vinay Hariharan-Problem solver and logical input of the team."
   about4="This project was started on 20th July 2021 and the first testing phase ended on"
   about6="30th November marking the completion of the project."
   about5="Overall, quite a fascinating project to work upon ,"
   about7="which included a lot of data structures and algorithms which were very time taking."

   a2=Label(window,text=about,bg="#103857",fg="white",font=("Algerian",20,"bold")).place(x=0,y=50)
   a2=Label(window,text=about1,bg="#103857",fg="white",font=("Algerian",20,"bold")).place(x=0,y=80)
   a2=Label(window,text=about2,bg="#103857",fg="white",font=("Algerian",20,"bold")).place(x=0,y=110)
   a2=Label(window,text=about3,bg="#103857",fg="white",font=("Algerian",20,"bold")).place(x=0,y=140)
   a2=Label(window,text=about4,bg="#103857",fg="white",font=("Algerian",20,"bold")).place(x=0,y=170)
   a2=Label(window,text=about6,bg="#103857",fg="white",font=("Algerian",20,"bold")).place(x=0,y=200)
   a2=Label(window,text=about5,bg="#103857",fg="white",font=("Algerian",20,"bold")).place(x=0,y=230)
   a2=Label(window,text=about7,bg="#103857",fg="white",font=("Algerian",20,"bold")).place(x=0,y=260)
   

   
   
def reportgen(): #This is for the admin to manage the accounts
   global lb
   window = Tk()
   window.title("Users")
   window.config(bg="#333333")
   window.geometry('900x600')
   Button(window,width=0,text='back',bg="#201328",fg="white",border=1,font=("ariel black",10,"bold"),command=main).place(x=750,y=0)

   def selected_item():
       for i in lb.curselection():
           print(lb.get(i))

   def remove_item():
       for i in lb.curselection():
           a=(lb.get(i))
           b=a[0]
           lb.delete(i)
           cursor=mycon.cursor()
           cursor.execute("delete from login where user='"+b+"'" )
           cursor.execute("drop table "+b)
           mycon.commit()
           
   def InfoButton():
      
       for i in lb.curselection():
           a=(lb.get(i))
           b=a[0]
           cursor=mycon.cursor()
           cursor.execute("select sent,recieved from "+b)
           data = cursor.fetchall()

       from tkinter import ttk
       root=Tk()
       root.title('Accounts')
       root.geometry('1000x700')
       root.configure(bg="#333333")

       s = ttk.Style()
       s.theme_use('clam')

       tree = ttk.Treeview(root, column=("c1", "c2"), show='headings', height=20)

       tree.column("# 1", anchor=CENTER)
       tree.heading("# 1", text="SENT")
       tree.column("# 2", anchor=CENTER)
       tree.heading("# 2", text="RECIEVED")

       a1=Label(root,text='Details',bg="#333333",fg="white",font=("Algerian",30,"bold"))
       a1.place(x=10,y=10)
       for i in range(0,len(data),1):
           tree.insert('', 'end', text="i", values=data[i])
           
       tree.place(x=20,y=100)

   def SendButton():
      global body
      root=Tk()
      root.title('New message')
      root.geometry('800x500')
      root.configure(bg="#333333")
      body=Text(root,width=80,height=10,fg='white',bg='grey',font=("ariel"))
      body.place(x=50,y=100)
      
      def send():
           messg=body.get("1.0",'end')
           for i in lb.curselection():
              a=(lb.get(i))
              un=a[0] 
              b=open(un,"a+")
              b.write("admin"+":-"+messg)
              b.write("%s"%now)
              b.write("\n")
              messagebox.showinfo("","Message sent")
             
      Button(root,width=20,text='Send',bg='grey',fg='white',border=1,font=("ariel black",10,"bold"),command=send).place(x=50,y=350)
      root.mainloop

   def clr():
      cursor=mycon.cursor()
      cursor.execute("delete from login")
      for user in allu:
         cursor.execute("drop table "+user[0])   
      mycon.commit()
      lb.delete(0,"end")
          
   head = Label(window, text="Users", font=("algerian", 36, "bold"), fg="white", bg="#333333")
   head.place(x=0,y=0)

   lblfirstname = Label(window, text="This statistics will tell you about all the necessary information of the server", font=("Calibri", 14, "bold"), fg="white", bg="#333333")
   lblfirstname.place(x=10,y=100)

   InfoButton = Button(window,text="Details",width=12, font=("Calibri", 10, "italic"), fg="white", bg="#333333",command = InfoButton, relief=RIDGE, bd=10)
   InfoButton.place(x=10,y=150)

   SendButton = Button(window,text="Send mail",width=12, font=("Calibri", 10, "italic"), fg="white", bg="#333333",command=SendButton, relief=RIDGE, bd=10)
   SendButton.place(x=110,y=150)

   ViewAllButton = Button(window,text="View All",width=12, font=("Calibri", 10, "italic"), fg="white", bg="#333333",command=displayacc, relief=RIDGE, bd=10)
   ViewAllButton.place(x=220,y=150)

   DeleteButton = Button(window,text="Delete",width=12, font=("Calibri", 10, "italic"), fg="white", bg="#333333",command=remove_item, relief=RIDGE, bd=10)
   DeleteButton.place(x=330,y=150)

   ClearAllButton = Button(window,text="Clear All",width=12, font=("Calibri", 10, "italic"), fg="white", bg="#333333",command=clr, relief=RIDGE, bd=10)
   ClearAllButton.place(x=440,y=150)

   lb=Listbox(window,height=20,width=94)
   lb.place(x=10,y=200)
   for i in range(0,len(allu),1):
      lb.insert(i,allu[i])

   sb=Scrollbar(window)
   sb.place(x=600,y=300)

   lb.configure(yscrollcommand=sb.set)
   sb.configure(command=lb.yview)
   
#main       

cursor=mycon.cursor()
dnt()

logininterface()
cursor=mycon.cursor()
cursor.execute("select user from login")
allu=cursor.fetchall()

       
