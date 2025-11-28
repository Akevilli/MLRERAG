--
-- PostgreSQL database cluster dump
--

-- Started on 2025-11-26 17:10:50

\restrict OcyUBi6cMP7GCXoaNf0h8ViU2HgYbIBXAp2Blac4adNJDT1IBLcl8cwMndlZ3zJ

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE "MLRERAG-RAG";
ALTER ROLE "MLRERAG-RAG" WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN NOREPLICATION BYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:44DkS11w8C2qo7YHcBVdiQ==$LIrrDs77TFAacvhYmABoq7M1KguwdyvkmAdDzi7wyCQ=:3gLLJr/o40lBeWv0hwa624HeWRxV7U8KXwjm672djOE=';
CREATE ROLE "MLRERAG-backend";
ALTER ROLE "MLRERAG-backend" WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN NOREPLICATION BYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:JV4icvms+7P3G1BS/nAHKA==$cInoRpuglscP7rFz/5SL18+HMej5NODY7u81PrrtvJc=:ePIcVYy0NkFDmsJPcU+Y7N9f2nzuY4tQouUULNsyXoI=';
--
-- User Configurations
--






\unrestrict OcyUBi6cMP7GCXoaNf0h8ViU2HgYbIBXAp2Blac4adNJDT1IBLcl8cwMndlZ3zJ

-- Completed on 2025-11-26 17:10:50

--
-- PostgreSQL database cluster dump complete
--

