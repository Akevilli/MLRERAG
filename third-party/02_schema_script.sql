--
-- PostgreSQL database dump
--

\connect MLRERAG;
CREATE EXTENSION IF NOT EXISTS vector;

\restrict V3nTSGXVgkF095CTF5GApeRprPjmKdLUUyYwj3uqeYNeC50D0UHofxNicT62egs

-- Dumped from database version 18.0
-- Dumped by pg_dump version 18.0

-- Started on 2025-11-28 21:37:16

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- TOC entry 222 (class 1259 OID 40991)
-- Name: chats; Type: TABLE; Schema: public; Owner: MLRERAG-backend
--

CREATE TABLE public.chats (
    title character varying NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    owner_id uuid NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE public.chats OWNER TO "MLRERAG-backend";

--
-- TOC entry 225 (class 1259 OID 41457)
-- Name: chunks; Type: TABLE; Schema: public; Owner: MLRERAG-RAG
--

CREATE TABLE public.chunks (
    id uuid NOT NULL,
    text character varying NOT NULL,
    embedding public.vector(384) NOT NULL,
    chunk_metadata jsonb NOT NULL
);


ALTER TABLE public.chunks OWNER TO "MLRERAG-RAG";

--
-- TOC entry 223 (class 1259 OID 41008)
-- Name: messages; Type: TABLE; Schema: public; Owner: MLRERAG-backend
--

CREATE TABLE public.messages (
    content character varying NOT NULL,
    created_at timestamp without time zone NOT NULL,
    is_users boolean NOT NULL,
    chat_id uuid NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE public.messages OWNER TO "MLRERAG-backend";

--
-- TOC entry 221 (class 1259 OID 40981)
-- Name: refresh_token; Type: TABLE; Schema: public; Owner: MLRERAG-backend
--

CREATE TABLE public.refresh_token (
    owner_id uuid NOT NULL,
    created_at timestamp without time zone NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    is_revoked boolean NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE public.refresh_token OWNER TO "MLRERAG-backend";

--
-- TOC entry 220 (class 1259 OID 40962)
-- Name: users; Type: TABLE; Schema: public; Owner: MLRERAG-backend
--

CREATE TABLE public.users (
    username character varying NOT NULL,
    email character varying NOT NULL,
    password bytea NOT NULL,
    is_activated boolean NOT NULL,
    activation_token bytea NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE public.users OWNER TO "MLRERAG-backend";

--
-- TOC entry 5118 (class 2606 OID 41002)
-- Name: chats chats_pkey; Type: CONSTRAINT; Schema: public; Owner: MLRERAG-backend
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_pkey PRIMARY KEY (id);


--
-- TOC entry 5122 (class 2606 OID 41467)
-- Name: chunks chunks_pkey; Type: CONSTRAINT; Schema: public; Owner: MLRERAG-RAG
--

ALTER TABLE ONLY public.chunks
    ADD CONSTRAINT chunks_pkey PRIMARY KEY (id);


--
-- TOC entry 5120 (class 2606 OID 41019)
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: MLRERAG-backend
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- TOC entry 5116 (class 2606 OID 40990)
-- Name: refresh_token refresh_token_pkey; Type: CONSTRAINT; Schema: public; Owner: MLRERAG-backend
--

ALTER TABLE ONLY public.refresh_token
    ADD CONSTRAINT refresh_token_pkey PRIMARY KEY (id);


--
-- TOC entry 5110 (class 2606 OID 40980)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: MLRERAG-backend
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 5112 (class 2606 OID 40976)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: MLRERAG-backend
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 5114 (class 2606 OID 40978)
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: MLRERAG-backend
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- TOC entry 5123 (class 1259 OID 41468)
-- Name: hnsw_chunk_embedding_idx; Type: INDEX; Schema: public; Owner: MLRERAG-RAG
--

CREATE INDEX hnsw_chunk_embedding_idx ON public.chunks USING hnsw (embedding public.vector_cosine_ops) WITH (m='16', ef_construction='128');


--
-- TOC entry 5124 (class 2606 OID 41003)
-- Name: chats chats_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: MLRERAG-backend
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 5125 (class 2606 OID 41020)
-- Name: messages messages_chat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: MLRERAG-backend
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES public.chats(id) ON UPDATE CASCADE ON DELETE CASCADE;


-- Completed on 2025-11-28 21:37:16

--
-- PostgreSQL database dump complete
--

\unrestrict V3nTSGXVgkF095CTF5GApeRprPjmKdLUUyYwj3uqeYNeC50D0UHofxNicT62egs

