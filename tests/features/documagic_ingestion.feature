Feature: DocuMagic email ingestion for charitable society documents
  As a DocuMagic admin of the charitable society
  I want email attachments to be ingested and stored as documents
  So that beneficiary records and documents are centralized in the system

  Background:
    Given the PostgreSQL database is running
    And the "documents" and "users" tables exist
    And a user with id 1 exists as the system owner
    And the IMAP inbox "documagic_charity_society@zohomail.in" is reachable

  Scenario: Ingest unread emails and store attachments as documents
    Given there are unread emails in the charity inbox with PDF attachments
    When the ingestion API "/ingest/run" is called
    Then the API should respond with status 200
    And the response should contain "processed_count" greater than or equal to 1
    And each processed item should include "uid", "subject", "from", and "attachments"
    And each attachment path from the response should correspond to a file on disk
    And for each saved attachment a new row should exist in the "documents" table
