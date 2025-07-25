# Source Analysis Template

This template defines what sources to analyze and what knowledge to extract. Based on the Gemini context engineering INITIAL.md pattern.

## CODEBASE TO ANALYZE:

**Primary Source Code:**
- Backend services: `./backend/`, `./api/`, `./server/`
- Frontend code: `./frontend/`, `./client/`, `./web/`
- Database schemas: `./migrations/`, `./schemas/`
- Configuration: `./config/`, `./settings/`

**Documentation Sources:**
- README files: `./README.md`, `./docs/README.md`
- API documentation: `./docs/api/`, `./openapi.yaml`, `./swagger.json`
- Architecture docs: `./docs/architecture/`, `./ARCHITECTURE.md`
- Setup guides: `./docs/setup/`, `./INSTALL.md`

**Execution Data:**
- Application logs: `./logs/`, `./var/log/`
- Error logs: `./errors/`, `./crash_reports/`
- Performance logs: `./metrics/`, `./monitoring/`
- Test execution results: `./test_results/`, `./coverage/`

**Visual Materials:**
- Architecture diagrams: `./diagrams/`, `./docs/images/`
- UI mockups: `./designs/`, `./mockups/`
- Flow charts: `./flows/`, `./process_diagrams/`
- Screenshots: `./screenshots/`, `./examples/`

**API & Integration:**
- API specifications: `./api_specs/`, `./swagger/`
- Third-party integrations: `./integrations/`, `./external/`
- Database schemas: `./db/`, `./models/`
- Message queues: `./queues/`, `./events/`

## KNOWLEDGE EXTRACTION GOALS:

**Implementation Guides:**
- How to build user authentication system
- How to implement API rate limiting
- How to set up database connections
- How to handle file uploads
- How to implement real-time features
- How to structure error handling

**Architecture Understanding:**
- How the microservices communicate
- How data flows through the system
- How caching is implemented
- How background jobs are processed
- How deployment is structured

**Pattern Recognition:**
- Common code patterns and structures
- Reusable components and utilities
- Testing strategies and approaches
- Security implementation patterns
- Performance optimization techniques

**Gotcha Documentation:**
- Common failure points and solutions
- Configuration pitfalls to avoid
- Integration challenges and workarounds
- Performance bottlenecks and fixes
- Security vulnerabilities and mitigations

## OUTPUT FOCUS:

**Tutorial Style:** Each generated .md should be a comprehensive "how to build X" guide
**Educational Depth:** Include reasoning behind architectural decisions
**Practical Examples:** Real code snippets with explanations
**Complete Coverage:** Implementation + testing + deployment + monitoring

## EXAMPLES TO EXTRACT:

List specific features or systems you want comprehensive guides for:

- User registration and authentication flow
- Payment processing implementation
- Real-time chat/messaging system
- File upload and storage handling
- API design and versioning strategy
- Database optimization patterns
- Caching strategy implementation
- Error handling and logging system
- Background job processing
- Email/notification system

## DOCUMENTATION PRIORITIES:

**High Priority:** Core business logic and user-facing features
**Medium Priority:** Infrastructure and supporting systems  
**Low Priority:** Development tools and build processes

## OTHER CONSIDERATIONS:

**Technology Stack:** [List primary technologies, frameworks, and tools used]
**Team Size:** [Small/Medium/Large - affects complexity of patterns]
**Domain:** [Web app, API, mobile backend, etc. - affects focus areas]
**Complexity Level:** [Simple/Moderate/Complex - affects tutorial depth]

**Special Requirements:**
- Focus on specific programming languages or frameworks
- Emphasize security or performance aspects
- Include mobile-specific implementations
- Cover DevOps and deployment patterns

**Known Challenges:**
- Complex business logic areas that need extra explanation
- Integration points that commonly cause issues
- Performance-critical sections requiring optimization
- Legacy code areas that need modernization guidance

---

## Instructions for Use:

1. **Fill out all relevant sections** with specific paths and details for your project
2. **Be specific about extraction goals** - what do you want to learn how to build?
3. **List concrete examples** rather than generic categories
4. **Consider your audience** - who will use these tutorial guides?
5. **Run the extraction process** once this template is complete

This will generate a comprehensive knowledge library with detailed "how to build" guides based on your actual codebase.