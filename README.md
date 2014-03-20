Grep Twitter
--
A small utility program to try out PostgreSQL DB and the support for JSON data type introduced in v9.3.
Performs keyword-search on twitter, stores resulting tweet json data in PostgreSQL DB.

---

Create following two tables in your db:
```sql
CREATE TABLE tweets_db (id serial, data json, search_id integer);
CREATE TABLE tweets_metadb (id serial, start_time varchar(20), end_time varchar(20), search_mode smallint, keywords varchar(200));
```
(Notice that I am directly storing JSON data into db, without splitting fields.)

The db connection params & Twitter keys go into **keys.cnf** config file. 

With above setup, program can be launched as shown below:

```
Usage: python search.py <mode:forward|backward> <keyword1, keyword2..>
```
Two search modes are supported: `backward` & `forward` (using Search API & Streaming API respectively).

---

JSON Support in PostgreSQL is pretty impressive. With the newly collected data in JSON format, I could run following SQL queries to filter it based on some basic criteria - something that I would have done in code otherwise. 

* In the downloaded data see how many of the tweets have/ do not have geo tags: 

```sql
select count(*) from tweets_db where (data->>'geo') is not null;
select count(*) from tweets_db where (data->>'geo') is null;
```

* Search for the keywords in tweets

```sql
select data->>'text' from tweets_db where data->>'text' LIKE '%bod%' limit 20;
```

* Show only unique tweets

```sql
select count(distinct(data->>'id_str')) from tweets_db;
```

* Filter tweets by date of creation 

```sql
select data->>'id_str', data->>'created_at'::text as time from tweets_db where to_date(data->>'created_at'::text,'Dy Mon DD HH24:MI:SS +0000 YYYY')<'2014-03-18' limit 20;
```

These were some basics queries I tried. Ofcourse you could do more by using powerful SQL operators and functions on JSON data. 
