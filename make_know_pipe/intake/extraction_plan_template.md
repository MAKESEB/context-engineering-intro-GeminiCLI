# Knowledge Extraction Plan Template

Generated from SOURCE_ANALYSIS.md - this is the equivalent of a PRP for knowledge extraction.

## EXTRACTION OVERVIEW

**Project:** [Project Name]
**Analysis Date:** [Date]
**Extraction Goals:** [Primary goals from SOURCE_ANALYSIS.md]

## KNOWLEDGE EXTRACTION STRATEGY

### Phase 1: Source Code Analysis
**Target Areas:**
- Authentication system implementation
- API endpoint patterns and structures
- Database interaction patterns
- Error handling approaches
- Configuration management

**Analysis Approach:**
- Parse code structure and identify key modules
- Extract implementation patterns and architectural decisions
- Document code organization and conventions
- Identify reusable components and utilities

**Expected Outputs:**
- `how_to_build/authentication_system.md`
- `patterns/api_endpoint_patterns.md`
- `patterns/database_interaction.md`
- `gotchas/error_handling_pitfalls.md`

### Phase 2: Documentation Processing
**Target Materials:**
- API documentation and specifications
- Architecture decision records
- Setup and deployment guides
- README files and technical docs

**Analysis Approach:**
- Extract architectural reasoning and decisions
- Document integration patterns and dependencies
- Identify setup procedures and requirements
- Extract troubleshooting information

**Expected Outputs:**
- `architecture/system_design_decisions.md`
- `how_to_build/deployment_setup.md`
- `gotchas/common_setup_issues.md`

### Phase 3: Execution Data Analysis
**Target Data:**
- Application logs and error patterns
- Performance metrics and bottlenecks
- Test results and coverage reports
- Monitoring and alerting data

**Analysis Approach:**
- Identify common failure patterns
- Extract performance optimization insights
- Document monitoring and alerting strategies
- Analyze testing approaches and coverage

**Expected Outputs:**
- `gotchas/production_failure_patterns.md`
- `how_to_build/monitoring_and_alerting.md`
- `patterns/performance_optimization.md`

### Phase 4: Visual Material Processing
**Target Materials:**
- Architecture diagrams and flowcharts
- UI mockups and design specifications
- Process diagrams and workflows
- Screenshots and examples

**Analysis Approach:**
- Extract architectural insights from diagrams
- Document user interface patterns
- Understand process flows and workflows
- Identify visual design patterns

**Expected Outputs:**
- `architecture/visual_system_overview.md`
- `patterns/ui_implementation_guide.md`
- `how_to_build/workflow_implementation.md`

## DETAILED EXTRACTION TASKS

### Task 1: Authentication System Deep Dive
**Sources:** 
- `./backend/auth/`, `./api/auth/`
- `./docs/security.md`
- Auth-related error logs

**Knowledge to Extract:**
- User registration flow implementation
- Login/logout mechanisms
- Token management (JWT, sessions, etc.)
- Password hashing and validation
- Role-based access control
- OAuth integration patterns

**Output Structure:**
```markdown
# How to Build an Authentication System

## Architecture Overview
[System design decisions and reasoning]

## Step-by-Step Implementation
### 1. User Model and Database Schema
### 2. Password Hashing Setup
### 3. JWT Token Management
### 4. Login/Logout Endpoints
### 5. Protected Route Middleware
### 6. Role-Based Access Control

## Common Pitfalls and Solutions
## Testing Strategy
## Security Considerations
## Performance Optimization
```

### Task 2: API Design Pattern Extraction
**Sources:**
- All API endpoint files
- OpenAPI/Swagger specifications
- API-related documentation

**Knowledge to Extract:**
- REST API design patterns
- Request/response structure conventions
- Error handling and status codes
- Validation and sanitization approaches
- Rate limiting implementation
- API versioning strategy

**Output Structure:**
```markdown
# API Design Patterns Guide

## Design Philosophy
## Endpoint Structure Conventions
## Request/Response Patterns
## Error Handling Strategy
## Validation Approaches
## Rate Limiting Implementation
## Versioning Strategy
## Testing API Endpoints
```

### Task 3: Database Integration Analysis
**Sources:**
- Database models and schemas
- Migration files
- Database-related code
- Performance logs

**Knowledge to Extract:**
- Database schema design decisions
- ORM patterns and usage
- Query optimization techniques
- Connection pooling setup
- Migration strategies
- Backup and recovery approaches

## VALIDATION CRITERIA

**Quality Checks:**
- [ ] Each tutorial includes complete implementation steps
- [ ] Architectural decisions are explained with reasoning
- [ ] Common pitfalls are documented with solutions
- [ ] Code examples are complete and functional
- [ ] Testing strategies are included
- [ ] Performance considerations are covered

**Completeness Checks:**
- [ ] All major systems have comprehensive guides
- [ ] Integration points are well-documented
- [ ] Gotchas from logs/errors are captured
- [ ] Visual materials are properly analyzed
- [ ] Patterns are reusable and well-explained

## SUCCESS METRICS

**Educational Value:**
- Someone should be able to build a similar system using these guides
- Architectural reasoning should be clear and well-documented
- Common mistakes should be preventable with gotcha documentation

**Completeness:**
- Major features have step-by-step implementation guides
- System architecture is thoroughly documented
- Integration patterns are reusable

**Practicality:**
- Code examples are complete and functional
- Setup instructions are detailed and accurate
- Troubleshooting information is comprehensive

---

## Execution Plan

1. **Preparation:** Validate all source paths and materials
2. **Sequential Processing:** Execute tasks in dependency order
3. **Quality Review:** Validate outputs against criteria
4. **Integration:** Ensure guides reference each other appropriately
5. **Final Organization:** Structure knowledge library for easy navigation

This extraction plan will generate a comprehensive knowledge library teaching others how to build similar systems based on your real implementation.