-- ==============================================================
--  LE CHAMPION SUPERMARCHÉ TOGO
--  Script SQL de création de la base de données
--  PostgreSQL 16+ (ICU locale)
--
--  Exécution : psql -U postgres -f db_setup.sql
-- ==============================================================


-- ==============================================================
-- 1. SUPPRESSION (si recréation propre)
-- ==============================================================

-- Fermer toutes les connexions actives sur la base
SELECT pg_terminate_backend(pid)
FROM   pg_stat_activity
WHERE  datname = 'champion'
  AND  pid <> pg_backend_pid();

-- Supprimer la base et l'utilisateur s'ils existent déjà
DROP DATABASE IF EXISTS champion;
DROP ROLE     IF EXISTS klaus;


-- ==============================================================
-- 2. CRÉATION DU SUPERUTILISATEUR KLAUS
-- ==============================================================

CREATE ROLE klaus
    WITH
        SUPERUSER           -- Tous les droits administrateur
        CREATEDB            -- Peut créer des bases
        CREATEROLE          -- Peut créer des rôles
        INHERIT             -- Hérite des droits des rôles assignés
        LOGIN               -- Peut se connecter
        REPLICATION         -- Droits de réplication
        BYPASSRLS           -- Contourne les politiques RLS
        CONNECTION LIMIT -1 -- Connexions illimitées
    PASSWORD 'Klaus@Champion2024!';

COMMENT ON ROLE klaus IS
    'Superutilisateur propriétaire de la base champion — Le Champion Supermarché Togo';


-- ==============================================================
-- 3. CRÉATION DE LA BASE DE DONNÉES CHAMPION
-- ==============================================================

CREATE DATABASE champion
    WITH
        OWNER            = klaus
        ENCODING         = 'UTF8'
        ICU_LOCALE       = 'fr-FR'          -- Tri et règles françaises
        LOCALE_PROVIDER  = 'icu'            -- Moteur ICU (PostgreSQL 16+)
        TEMPLATE         = template0        -- Base vierge sans héritage
        CONNECTION LIMIT = -1;             -- Connexions illimitées

COMMENT ON DATABASE champion IS
    'Base de données du site vitrine — Le Champion Supermarché Togo';


-- ==============================================================
-- 4. CONNEXION À LA BASE ET CONFIGURATION DES DROITS
-- ==============================================================

\connect champion

-- Accorder tous les privilèges sur la base
GRANT ALL PRIVILEGES ON DATABASE champion TO klaus;

-- Accès complet au schéma public
GRANT ALL PRIVILEGES ON SCHEMA public TO klaus;

-- Rendre Klaus propriétaire du schéma public
ALTER SCHEMA public OWNER TO klaus;

-- Droits par défaut sur TOUS les futurs objets créés dans public
ALTER DEFAULT PRIVILEGES FOR ROLE klaus IN SCHEMA public
    GRANT ALL PRIVILEGES ON TABLES    TO klaus;

ALTER DEFAULT PRIVILEGES FOR ROLE klaus IN SCHEMA public
    GRANT ALL PRIVILEGES ON SEQUENCES TO klaus;

ALTER DEFAULT PRIVILEGES FOR ROLE klaus IN SCHEMA public
    GRANT ALL PRIVILEGES ON FUNCTIONS TO klaus;

ALTER DEFAULT PRIVILEGES FOR ROLE klaus IN SCHEMA public
    GRANT ALL PRIVILEGES ON TYPES     TO klaus;


-- ==============================================================
-- 5. EXTENSIONS UTILES
-- ==============================================================

-- Génération d'UUID (utilisé pour les tokens de désinscription newsletter)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Recherche textuelle sans accents (ex : "epicerie" trouve "épicerie")
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Recherche floue par trigrammes (LIKE rapide, similarité)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Texte insensible à la casse (utile pour les emails)
CREATE EXTENSION IF NOT EXISTS "citext";


-- ==============================================================
-- 6. PARAMÈTRES DE PERFORMANCE (optionnel — profil développement)
-- ==============================================================

-- Augmenter la mémoire de travail pour les tris/jointures
ALTER DATABASE champion SET work_mem = '16MB';

-- Statistiques plus précises pour le planificateur
ALTER DATABASE champion SET default_statistics_target = 100;

-- Encodage client forcé en UTF-8
ALTER DATABASE champion SET client_encoding = 'UTF8';

-- Fuseau horaire Togo (UTC+0, pas de changement d'heure)
ALTER DATABASE champion SET timezone = 'Africa/Lome';


-- ==============================================================
-- 7. VÉRIFICATION FINALE
-- ==============================================================

\echo ''
\echo '══════════════════════════════════════════════════'
\echo '  ✅  BASE DE DONNÉES CHAMPION — RAPPORT FINAL'
\echo '══════════════════════════════════════════════════'

\echo ''
\echo '── Utilisateur Klaus ──────────────────────────────'
SELECT
    rolname        AS "Utilisateur",
    rolsuper       AS "Superuser",
    rolcreatedb    AS "CreateDB",
    rolcreaterole  AS "CreateRole",
    rolcanlogin    AS "Login",
    rolreplication AS "Replication",
    rolbypassrls   AS "BypassRLS"
FROM pg_roles
WHERE rolname = 'klaus';

\echo ''
\echo '── Base de données champion ───────────────────────'
SELECT
    datname          AS "Base",
    pg_catalog.pg_get_userbyid(datdba)    AS "Propriétaire",
    pg_encoding_to_char(encoding)         AS "Encodage",
    daticulocale                          AS "Locale ICU",
    pg_size_pretty(pg_database_size(datname)) AS "Taille"
FROM pg_database
WHERE datname = 'champion';

\echo ''
\echo '── Extensions installées ──────────────────────────'
SELECT extname AS "Extension", extversion AS "Version"
FROM   pg_extension
ORDER  BY extname;

\echo ''
\echo '══════════════════════════════════════════════════'
\echo '  Configuration Django (.env) :'
\echo '  DB_NAME=champion'
\echo '  DB_USER=klaus'
\echo '  DB_PASSWORD=Klaus@Champion2024!'
\echo '  DB_HOST=localhost'
\echo '  DB_PORT=5432'
\echo '══════════════════════════════════════════════════'
\echo ''