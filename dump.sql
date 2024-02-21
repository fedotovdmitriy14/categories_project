--
-- PostgreSQL database dump
--

-- Dumped from database version 13.12 (Debian 13.12-1.pgdg120+1)
-- Dumped by pg_dump version 14.10 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: app
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO app;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: app
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(50),
    level integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    children_ids json,
    parent_id integer
);


ALTER TABLE public.categories OWNER TO app;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: app
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.categories_id_seq OWNER TO app;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: app
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: app
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: app
--

COPY public.alembic_version (version_num) FROM stdin;
72b718c626d2
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: app
--

COPY public.categories (id, name, level, created_at, updated_at, children_ids, parent_id) FROM stdin;
15	подкатегория	2	2024-02-20 22:40:54.405011	2024-02-20 22:40:54.405019	[]	14
14	новая категория	1	2024-02-20 22:40:40.103404	2024-02-20 22:40:40.103447	[15]	\N
5	электроника	1	2024-02-20 19:42:54.030393	2024-02-20 19:42:54.030522	[12, 17, 18]	\N
18	периферия	2	2024-02-20 23:23:51.764397	2024-02-20 23:23:51.764413	[19]	5
20	проводные	4	2024-02-20 23:24:31.773166	2024-02-20 23:24:31.773179	[]	19
21	беспроводные	4	2024-02-20 23:24:41.652311	2024-02-20 23:24:41.652316	[]	19
19	наушники	3	2024-02-20 23:24:03.955611	2024-02-20 23:24:03.955629	[20, 21]	18
17	телефоны	2	2024-02-20 23:23:26.676107	2024-02-20 23:23:26.67613	[22]	5
23	4к	3	2024-02-20 23:25:17.04373	2024-02-20 23:25:17.043737	[]	12
12	телевизоры	2	2024-02-20 20:08:26.652245	2024-02-20 20:08:26.652259	[23]	5
\.


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: app
--

SELECT pg_catalog.setval('public.categories_id_seq', 24, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: app
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: app
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: categories unique_name; Type: CONSTRAINT; Schema: public; Owner: app
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT unique_name UNIQUE (name);


--
-- PostgreSQL database dump complete
--

