CREATE TABLE Korisnici(
br_racuna VARCHAR(18) PRIMARY KEY NOT NULL,
ime_prezime VARCHAR(50) NOT NULL,
stanje FLOAT NOT NULL,
pin VARCHAR(4) NOT NULL
);

DROP TABLE Korisnici

SELECT * FROM Korisnici

INSERT INTO Korisnici (br_racuna,ime_prezime,stanje,pin)
VALUES 
	('0000121212','Ana Nikolic',1500.00,'0123'),
	('0000212121','Marko Markovic',3300.00,'1212'),
	('0000303134','Petar Petrovic',700.50,'1313'),
	('2016400540','Ivana Ivanovic',650.99,'1414'),
	('0064005907','Nikola Nikolic',4860.57,'1515'),
	('6000879912','Nevena Jovanovic',5645.03,'1616');
	
	
CREATE TABLE Transakcije(
br_transakcije SERIAL NOT NULL,
ime_prezime_posiljaoca VARCHAR(50) NOT NULL,
ime_prezime_primaoca VARCHAR(50) NOT NULL,
br_racuna_posiljaoca VARCHAR(18) NOT NULL,
br_racuna_primaoca VARCHAR(18) NOT NULL,
iznos FLOAT NOT NULL,
PRIMARY KEY(br_transakcije),
FOREIGN KEY(br_racuna_posiljaoca) REFERENCES Korisnici(br_racuna),
FOREIGN KEY(br_racuna_primaoca) REFERENCES Korisnici(br_racuna));

DROP TABLE Transakcije
SELECT * FROM Transakcije

INSERT INTO Transakcije (br_transakcije,ime_prezime_posiljaoca,ime_prezime_primaoca,br_racuna_posiljaoca,br_racuna_primaoca,iznos)
VALUES 
	(1,'Ana Nikolic','Marko Markovic','0000121212','0000212121',150.00),
	(2,'Petar Petrovic','Nikola Nikolic','0000303134','0064005907',330.50),
	(3,'Nevena Jovanovic','Ivana Ivanovic','6000879912','2016400540',900.00);


UPDATE Korisnici AS k
SET stanje = 
    CASE 
        WHEN k.br_racuna = t.br_racuna_posiljaoca THEN k.stanje - t.iznos
        WHEN k.br_racuna = t.br_racuna_primaoca THEN k.stanje + t.iznos
        ELSE k.stanje
    END
FROM Transakcije AS t
WHERE k.br_racuna IN (t.br_racuna_posiljaoca, t.br_racuna_primaoca);



SELECT * FROM Korisnici

SELECT t.*, k.ime_prezime
FROM Transakcije as t 
JOIN Korisnici k ON t.br_racuna_posiljaoca = k.br_racuna;










