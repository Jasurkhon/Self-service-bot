BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "customer" (
	"id"	INTEGER,
	"first_name"	TEXT,
	"second_name"	TEXT,
	"email"	TEXT,
	"status"	INTEGER,
	PRIMARY KEY("id")
);
INSERT INTO "customer" VALUES (1,'Александр','Горбачев','alex@gmail.com',0);
INSERT INTO "customer" VALUES (2,'Жасурхон','Бахрамов','jasur.uzb10@gmail.com',1);
INSERT INTO "customer" VALUES (3,'Сардор','Иргашев','irgashevsardor99@gmail.com',1);
INSERT INTO "customer" VALUES (4,'Исмоил','Махамаджонов','imahamatdjanov@gmail.com',1);
INSERT INTO "customer" VALUES (5,'Иван','Соболев','ivan.sobolev@nexign.com',1);
COMMIT;
