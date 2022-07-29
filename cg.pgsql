--
-- PostgreSQL database dump
--

-- Dumped from database version 14.4
-- Dumped by pg_dump version 14.4

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

--
-- Name: admin_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.admin_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.admin_id_seq OWNER TO abyrondeans;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admin; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.admin (
    id integer DEFAULT nextval('public.admin_id_seq'::regclass) NOT NULL,
    password character varying(20) NOT NULL
);


ALTER TABLE public.admin OWNER TO abyrondeans;

--
-- Name: admin_logins_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.admin_logins_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.admin_logins_id_seq OWNER TO abyrondeans;

--
-- Name: admin_logins; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.admin_logins (
    id integer DEFAULT nextval('public.admin_logins_id_seq'::regclass) NOT NULL,
    time_logged_in integer NOT NULL,
    ip_logged_in character varying(128) NOT NULL
);


ALTER TABLE public.admin_logins OWNER TO abyrondeans;

--
-- Name: answers_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.answers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.answers_id_seq OWNER TO abyrondeans;

--
-- Name: answers; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.answers (
    id integer DEFAULT nextval('public.answers_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    lecture_video_id integer,
    question_id integer,
    answer character varying,
    created_on timestamp without time zone NOT NULL
);


ALTER TABLE public.answers OWNER TO abyrondeans;

--
-- Name: friends_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.friends_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.friends_id_seq OWNER TO abyrondeans;

--
-- Name: friends; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.friends (
    id integer DEFAULT nextval('public.friends_id_seq'::regclass) NOT NULL,
    user_id_requester integer NOT NULL,
    user_id_accepter integer NOT NULL,
    time_requested integer NOT NULL,
    time_deleted integer,
    time_accepted integer,
    time_denied integer
);


ALTER TABLE public.friends OWNER TO abyrondeans;

--
-- Name: investorinfo_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.investorinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.investorinfo_id_seq OWNER TO abyrondeans;

--
-- Name: investorinfo; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.investorinfo (
    id integer DEFAULT nextval('public.investorinfo_id_seq'::regclass) NOT NULL,
    name character varying(100) NOT NULL,
    accesscode character varying(255) NOT NULL,
    address character varying(100),
    phone character varying(30),
    email character varying(100),
    notes character varying(1000),
    timelimit integer,
    firstaccess integer,
    deleted boolean,
    expiry integer
);


ALTER TABLE public.investorinfo OWNER TO abyrondeans;

--
-- Name: investorpage_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.investorpage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.investorpage_id_seq OWNER TO abyrondeans;

--
-- Name: investorpage; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.investorpage (
    id integer DEFAULT nextval('public.investorpage_id_seq'::regclass) NOT NULL,
    investor_id integer NOT NULL,
    ip_address character varying(50) NOT NULL,
    page character varying(300) NOT NULL,
    "time" integer
);


ALTER TABLE public.investorpage OWNER TO abyrondeans;

--
-- Name: lecture_video_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.lecture_video_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lecture_video_id_seq OWNER TO abyrondeans;

--
-- Name: lecture_video; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.lecture_video (
    id integer DEFAULT nextval('public.lecture_video_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    created_on timestamp without time zone NOT NULL,
    video_address character varying,
    number_of_questions integer,
    description character varying,
    video_title character varying,
    completed integer,
    deleted boolean DEFAULT false,
    deleted_date integer,
    preapprove boolean
);


ALTER TABLE public.lecture_video OWNER TO abyrondeans;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.messages_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.messages_id_seq OWNER TO abyrondeans;

--
-- Name: messages; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.messages (
    id integer DEFAULT nextval('public.messages_id_seq'::regclass) NOT NULL,
    user_id_sender integer NOT NULL,
    user_id_receiver integer NOT NULL,
    message character varying(400),
    time_sent integer NOT NULL,
    time_viewed integer
);


ALTER TABLE public.messages OWNER TO abyrondeans;

--
-- Name: questions_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.questions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.questions_id_seq OWNER TO abyrondeans;

--
-- Name: questions; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.questions (
    id integer DEFAULT nextval('public.questions_id_seq'::regclass) NOT NULL,
    question character varying,
    answer character varying,
    choices character varying,
    created_on timestamp without time zone NOT NULL,
    lecture_video_id integer,
    question_number integer
);


ALTER TABLE public.questions OWNER TO abyrondeans;

--
-- Name: quiz_grades_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.quiz_grades_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quiz_grades_id_seq OWNER TO abyrondeans;

--
-- Name: quiz_grades; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.quiz_grades (
    id integer DEFAULT nextval('public.quiz_grades_id_seq'::regclass) NOT NULL,
    user_id integer,
    video_id integer,
    created_on timestamp without time zone NOT NULL,
    num_correct integer,
    num_total_questions integer
);


ALTER TABLE public.quiz_grades OWNER TO abyrondeans;

--
-- Name: quiz_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.quiz_questions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quiz_questions_id_seq OWNER TO abyrondeans;

--
-- Name: quiz_questions; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.quiz_questions (
    id integer DEFAULT nextval('public.quiz_questions_id_seq'::regclass) NOT NULL,
    lecture_video_id integer NOT NULL,
    user_id integer NOT NULL,
    question_id integer NOT NULL,
    answer_provided character varying(50) NOT NULL,
    question_num integer
);


ALTER TABLE public.quiz_questions OWNER TO abyrondeans;

--
-- Name: student_request_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.student_request_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.student_request_id_seq OWNER TO abyrondeans;

--
-- Name: student_request; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.student_request (
    id integer DEFAULT nextval('public.student_request_id_seq'::regclass) NOT NULL,
    student_id integer NOT NULL,
    instructor_id integer NOT NULL,
    video_id integer NOT NULL,
    date_requested integer NOT NULL,
    date_granted integer,
    permission boolean NOT NULL
);


ALTER TABLE public.student_request OWNER TO abyrondeans;

--
-- Name: user_profile_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.user_profile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_profile_id_seq OWNER TO abyrondeans;

--
-- Name: user_profile; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.user_profile (
    id integer DEFAULT nextval('public.user_profile_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    profile character varying(489)
);


ALTER TABLE public.user_profile OWNER TO abyrondeans;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO abyrondeans;

--
-- Name: users; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.users (
    id integer DEFAULT nextval('public.users_id_seq'::regclass) NOT NULL,
    username character varying,
    pwd character varying,
    created_on timestamp without time zone NOT NULL
);


ALTER TABLE public.users OWNER TO abyrondeans;

--
-- Name: video_comment_replies_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.video_comment_replies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.video_comment_replies_id_seq OWNER TO abyrondeans;

--
-- Name: video_comment_replies; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.video_comment_replies (
    id integer DEFAULT nextval('public.video_comment_replies_id_seq'::regclass) NOT NULL,
    video_comment_id integer NOT NULL,
    replying_user integer NOT NULL,
    created_on integer NOT NULL,
    reply character varying(355)
);


ALTER TABLE public.video_comment_replies OWNER TO abyrondeans;

--
-- Name: video_comments_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.video_comments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.video_comments_id_seq OWNER TO abyrondeans;

--
-- Name: video_comments; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.video_comments (
    id integer DEFAULT nextval('public.video_comments_id_seq'::regclass) NOT NULL,
    video_id integer NOT NULL,
    posting_user integer NOT NULL,
    created_on integer NOT NULL,
    comment character varying(355)
);


ALTER TABLE public.video_comments OWNER TO abyrondeans;

--
-- Name: wall_post_replies_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.wall_post_replies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.wall_post_replies_id_seq OWNER TO abyrondeans;

--
-- Name: wall_post_replies; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.wall_post_replies (
    id integer DEFAULT nextval('public.wall_post_replies_id_seq'::regclass) NOT NULL,
    wall_post_id integer NOT NULL,
    user_id integer NOT NULL,
    time_created integer NOT NULL,
    time_deleted integer,
    content character varying(355)
);


ALTER TABLE public.wall_post_replies OWNER TO abyrondeans;

--
-- Name: wall_posts_id_seq; Type: SEQUENCE; Schema: public; Owner: abyrondeans
--

CREATE SEQUENCE public.wall_posts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.wall_posts_id_seq OWNER TO abyrondeans;

--
-- Name: wall_posts; Type: TABLE; Schema: public; Owner: abyrondeans
--

CREATE TABLE public.wall_posts (
    id integer DEFAULT nextval('public.wall_posts_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    time_deleted integer,
    content character varying(455),
    time_created integer
);


ALTER TABLE public.wall_posts OWNER TO abyrondeans;

--
-- Name: admin_logins admin_logins_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.admin_logins
    ADD CONSTRAINT admin_logins_pkey PRIMARY KEY (id);


--
-- Name: admin admin_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.admin
    ADD CONSTRAINT admin_pkey PRIMARY KEY (id);


--
-- Name: answers answers_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.answers
    ADD CONSTRAINT answers_pkey PRIMARY KEY (id);


--
-- Name: friends friends_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.friends
    ADD CONSTRAINT friends_pkey PRIMARY KEY (id);


--
-- Name: investorinfo investorinfo_name_key; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.investorinfo
    ADD CONSTRAINT investorinfo_name_key UNIQUE (name);


--
-- Name: investorinfo investorinfo_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.investorinfo
    ADD CONSTRAINT investorinfo_pkey PRIMARY KEY (id);


--
-- Name: investorpage investorpage_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.investorpage
    ADD CONSTRAINT investorpage_pkey PRIMARY KEY (id);


--
-- Name: lecture_video lecture_video_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.lecture_video
    ADD CONSTRAINT lecture_video_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: questions questions_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (id);


--
-- Name: quiz_grades quiz_grades_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.quiz_grades
    ADD CONSTRAINT quiz_grades_pkey PRIMARY KEY (id);


--
-- Name: quiz_questions quiz_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.quiz_questions
    ADD CONSTRAINT quiz_questions_pkey PRIMARY KEY (id);


--
-- Name: student_request student_request_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.student_request
    ADD CONSTRAINT student_request_pkey PRIMARY KEY (id);


--
-- Name: user_profile user_profile_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.user_profile
    ADD CONSTRAINT user_profile_pkey PRIMARY KEY (id);


--
-- Name: user_profile user_profile_user_id_key; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.user_profile
    ADD CONSTRAINT user_profile_user_id_key UNIQUE (user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: video_comment_replies video_comment_replies_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.video_comment_replies
    ADD CONSTRAINT video_comment_replies_pkey PRIMARY KEY (id);


--
-- Name: video_comments video_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.video_comments
    ADD CONSTRAINT video_comments_pkey PRIMARY KEY (id);


--
-- Name: wall_post_replies wall_post_replies_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.wall_post_replies
    ADD CONSTRAINT wall_post_replies_pkey PRIMARY KEY (id);


--
-- Name: wall_posts wall_posts_pkey; Type: CONSTRAINT; Schema: public; Owner: abyrondeans
--

ALTER TABLE ONLY public.wall_posts
    ADD CONSTRAINT wall_posts_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

