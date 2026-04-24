# Story Review Checklist

Use this checklist when reviewing stories for quality and completeness.

## INVEST Principles
- [ ] **Independent** - Can be developed without dependencies on other stories
- [ ] **Negotiable** - Details can be discussed and refined
- [ ] **Valuable** - Delivers clear value to the user/business
- [ ] **Estimable** - Can be estimated by the development team
- [ ] **Small** - Completable by one developer in 8-12h including tests
- [ ] **Testable** - Has clear, verifiable acceptance criteria

## Vertical Slice Coverage
- [ ] App/UI Layer addressed
- [ ] Service/API Layer addressed
- [ ] Database Layer addressed
- [ ] NOT a horizontal story (DB-only, API-only, or UI-only)

## Acceptance Criteria Quality
- [ ] Uses Given-When-Then format
- [ ] Has 2-5 acceptance criteria
- [ ] Covers happy path scenarios
- [ ] Covers at least one edge case/error scenario
- [ ] Each criterion is independently testable
- [ ] No vague criteria like "it works correctly"
