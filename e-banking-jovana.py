import psycopg2 as pg
import pandas as pd
from tkinter import *
from tkinter import messagebox
import pyperclip

root = Tk()
root.title('E-Banking')


class EBanking:
    def __init__(self):
        self.con=pg.connect(
            database='E-Banking',
            host='localhost',
            port='5432',
            user='postgres',
            password='Yoyoba22'
            )
        self.korisnik_df=None
        self.tren_korisnik=None
        self.izvod_df=None
        self.upit=None
    
    def get_korisnik(self):
        self.korisnik_df=pd.read_sql_query('SELECT * FROM Korisnici',self.con)

    
    def ucitaj_korisnik(self):
        k_br_racuna=self.korisnik_df['br_racuna']
        k_ime_prezime=self.korisnik_df['ime_prezime']
        k_stanje=self.korisnik_df['stanje']
        k_pin=self.korisnik_df['pin']
        k=k_br_racuna.astype('string')+'|'+k_ime_prezime.astype('string')+'|'+k_stanje.astype('string')+'|'+k_pin.astype('string')

        return k.tolist()
    
    def ucitaj_ime(self,ime_prezime):
        korisnik_row=self.korisnik_df.loc[self.korisnik_df['ime_prezime']==ime_prezime,'ime_prezime']
        if korisnik_row.empty:
            return korisnik_row.values[0]
        else:
            return None
    
    def login(self,ime_prezime,pin):
        if self.tren_korisnik==None:
            p=False
            for _, row in self.korisnik_df.iterrows():
                if row['ime_prezime']==ime_prezime and row['pin']==pin:
                    p=True
                    self.tren_korisnik=ime_prezime
                    break
            if p:
                login_korisnik(ime_prezime)
                ime = E.ucitaj_ime(ime_prezime)
                if ime is not None:
                    result = self.execute_br_racuna(ime_prezime)
                    stanje=self.execute_stanje(ime_prezime)
                    login_korisnik(ime, result)
                    login_korisnik(ime,stanje)
                    uplata(ime,result)
                    pop_up_1(ime,stanje)
                    print('Dobro dosli {}'.format(ime))
            else:
                print('Korisnik sa tim kredencijalima ne postoji.')
    
    def uplata_na_racun(self, ime_prezime_posiljaoca, ime_prezime_primaoca, br_racuna_posiljaoca, br_racuna_primaoca, iznos):
        if self.tren_korisnik != None:
            if ime_prezime_posiljaoca == self.tren_korisnik:
                cursor = self.con.cursor()
                query = "INSERT INTO Transakcije (ime_prezime_posiljaoca, ime_prezime_primaoca, br_racuna_posiljaoca, br_racuna_primaoca, iznos) VALUES (%s, %s, %s, %s, %s) RETURNING br_transakcije"
                vrednosti = (ime_prezime_posiljaoca, ime_prezime_primaoca, br_racuna_posiljaoca, br_racuna_primaoca, float(iznos))
                cursor.execute(query, vrednosti)
                br_transakcije = cursor.fetchone()[0]
                self.con.commit()
                cursor.close()
                self.update_stanje()
                pop_up_1(ime_prezime_posiljaoca)


    def update_stanje(self):
        cursor = self.con.cursor()
        query = '''
            UPDATE Korisnici AS k
            SET stanje = 
                CASE 
                    WHEN k.br_racuna = t.br_racuna_posiljaoca THEN k.stanje - t.iznos
                    WHEN k.br_racuna = t.br_racuna_primaoca THEN k.stanje + t.iznos
                    ELSE k.stanje
                END
            FROM Transakcije AS t
            WHERE t.br_transakcije = (
                SELECT MAX(br_transakcije) FROM Transakcije
            );
        '''
        cursor.execute(query)
        self.con.commit()
        cursor.close()
        print("Stanje updated successfully")
        print(self.korisnik_df)
    
    def get_izvod(self):
        if self.tren_korisnik is not None:
            query = f'''
                SELECT t.*, k.stanje
                FROM Transakcije AS t
                JOIN Korisnici AS k ON t.br_racuna_posiljaoca = k.br_racuna
                WHERE k.ime_prezime = %s
            '''
            self.izvod_df = pd.read_sql_query(query, self.con, params=(self.tren_korisnik,))
            self.izvod_df.to_excel('izvod {}.xlsx'.format(self.tren_korisnik), index=False)
            pop_up_2()
        
    
    def execute_br_racuna(self, ime_prezime):
        query = "SELECT br_racuna FROM korisnici WHERE ime_prezime = %s"
        cursor = self.con.cursor()
        cursor.execute(query, (ime_prezime,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    
    def execute_stanje(self, ime_prezime):
        query = "SELECT stanje FROM korisnici WHERE ime_prezime = %s"
        cursor = self.con.cursor()
        cursor.execute(query, (ime_prezime,))
        stanje = cursor.fetchone()
        cursor.close()
        return stanje[0] if stanje else None
    
    def logout(self):
        if self.tren_korisnik!=None:
            self.tren_korisnik=None
            print('Uspesno odjavljivanje')
            root.destroy()
        else:
            print('Nije ulogovan nijedan korisnik')

        
    def update_stanje_and_label(self, label):
        updated_stanje = self.execute_stanje(self.tren_korisnik)
        label.config(text='Stanje: {} dinara'.format(updated_stanje))
        label.after(1000, self.update_stanje_and_label, label)

    def start_label_update(self, label):
        self.update_stanje_and_label(label)
            

E=EBanking()
E.get_korisnik()
E.ucitaj_korisnik()
#E.login('Ana Nikolic','0123')
#E.uplata_na_racun('Ana Nikolic','Marko Markovic','0000121212','0000212121',30)
#E.get_izvod()
 


def create_login_window(E):
    l1=Label(root,text='Ime i Prezime')
    l1.pack()
    e1=Entry(root)
    e1.pack()
    l2=Label(root,text='PIN')
    l2.pack()
    e2=Entry(root)
    e2.pack()
    b1=Button(root,text='Uloguj se',command=lambda:E.login(e1.get(), e2.get()))
    b1.pack()

create_login_window(E)



def login_korisnik(ime_prezime):
    global stanje,l2
    t=Toplevel()
    l2 = None
    result = E.execute_br_racuna(ime_prezime)
    stanje=E.execute_stanje(ime_prezime)
    if ime_prezime:
        t.title('Dobro dosli: {}'.format(ime_prezime))
        copy_icon = Label(t, text='\u2398', font='Arial 10', cursor='hand2')
        copy_icon.pack()
        copy_icon.bind('<Button-1>', lambda event: copy_to_clipboard(result))
        l1=Label(t,text='Broj Racuna: {}'.format(result))
        l1.pack()
        l2=Label(t,text='Stanje: {} dinara'.format(stanje))
        l2.pack()
        b=Button(t,text='Uplata na racun',command=lambda:uplata(ime_prezime))
        b.pack()
        menubar=Menu(t)
        e=Menu(menubar,tearoff=0)
        e.add_command(label='Preuzmi izvod',command=lambda:E.get_izvod())
        menubar.add_cascade(label='Izvestaj',menu=e)
        o=Menu(menubar,tearoff=0)
        o.add_command(label='Odjavljivanje',command=lambda:E.logout())
        menubar.add_cascade(label='Odjava',menu=o)
        t.config(menu=menubar)
        E.update_stanje_and_label(l2)
    else:
        messagebox.showerror("Login Error", "Korisnik sa tim kredencijalima ne postoji.")


def copy_to_clipboard(text):
    pyperclip.copy(text)
    print("Copied to clipboard:", text)

def uplata(ime_prezime):
    t=Toplevel()
    result=E.execute_br_racuna(ime_prezime)
    if ime_prezime:
        l1=Label(t,text='Ime i Prezime Posiljaoca: ')
        l1.grid(row=0,column=0)
        e1=Entry(t)
        e1.insert(END,ime_prezime)
        e1.grid(row=0,column=1)
        l2=Label(t,text='Ime i Prezime Primaoca: ')
        l2.grid(row=1,column=0)
        e2=Entry(t)
        e2.grid(row=1,column=1)
        l3=Label(t,text='Broj racuna posiljaoca: ')
        l3.grid(row=2,column=0)
        e3=Entry(t)
        e3.insert(END,result)
        e3.grid(row=2,column=1)
        l4=Label(t,text='Broj racuna primaoca: ')
        l4.grid(row=3,column=0)
        e4=Entry(t)
        e4.grid(row=3,column=1)
        l5=Label(t,text='Iznos za uplatu RSD: ')
        l5.grid(row=4,column=0)
        e5=Entry(t)
        e5.grid(row=4,column=1)
        b=Button(t,text='Izvrsi uplatu',command=lambda:E.uplata_na_racun(e1.get(),e2.get(),e3.get(),e4.get(),e5.get()))
        b.grid(row=5,column=0)

def pop_up_1(ime_prezime_posiljaoca):
    t=Toplevel()
    stanje=E.execute_stanje(ime_prezime_posiljaoca)
    if ime_prezime_posiljaoca:
        l=Label(t,text='Uplata uspesno izvrsena, novo stanje na racunu: {} RSD'.format(stanje))
        l.pack()

def pop_up_2():
    t=Toplevel()
    l=Label(t,text='Izvod uspesno kreiran')
    l.pack()






mainloop()