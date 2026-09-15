-- Tabela de agendamentos da clinica
-- IDENTITY column: chave primaria com auto-incremento nativo (Oracle 12c+),
-- dispensa a criacao manual de SEQUENCE + TRIGGER.
-- UNIQUE(APPOINTMENT_DATE, APPOINTMENT_TIME): garante no banco que nao existam
-- dois agendamentos para o mesmo dia/horario, mesmo em caso de concorrencia.

CREATE TABLE APPOINTMENTS (
    ID                NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    PATIENT_NAME      VARCHAR2(150) NOT NULL,
    PATIENT_PHONE     VARCHAR2(20),
    APPOINTMENT_DATE  DATE NOT NULL,
    APPOINTMENT_TIME  VARCHAR2(5) NOT NULL,
    STATUS            VARCHAR2(20) DEFAULT 'CONFIRMED' NOT NULL,
    CREATED_AT        TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT UQ_APPOINTMENT_SLOT UNIQUE (APPOINTMENT_DATE, APPOINTMENT_TIME)
);
