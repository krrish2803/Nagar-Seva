# NagarSeva Architecture

This document visualizes the major system components, user flow, AI-agent workflow, backend API structure, and deployment model.

## High-Level System Architecture

```mermaid
flowchart LR
    Citizen["Citizen Web User"] --> Frontend["Next.js Frontend"]
    Frontend --> Proxy["Next.js API Proxy Routes"]
    Proxy --> Backend["FastAPI Backend"]

    Backend --> Auth["JWT Authentication"]
    Backend --> ComplaintAPI["Complaint APIs"]
    Backend --> AnalyticsAPI["Analytics APIs"]
    Backend --> RouteAPI["Route Advisor APIs"]
    Backend --> EscalationAPI["Escalation APIs"]

    ComplaintAPI --> Storage["Media Storage"]
    ComplaintAPI --> MongoDB[("MongoDB Atlas")]
    ComplaintAPI --> Agents["AI Agent Layer"]

    Agents --> Classification["Voice + Image Classification"]
    Agents --> Trust["AI Trust Scoring"]
    Agents --> Routing["Authority Routing"]
    Agents --> Progress["AI Progress Updates"]
    Agents --> Heatmap["Heatmap Clustering"]
    Agents --> Escalation["Escalation Engine"]

    Classification --> NVIDIA["NVIDIA NIM"]
    Progress --> NVIDIA
    Trust --> MongoDB
    Routing --> MongoDB
    Heatmap --> MongoDB
    Escalation --> MongoDB

    Backend --> Notifications["Email / SMS / Push Utilities"]
```

## Citizen Reporting Flow

```mermaid
sequenceDiagram
    actor Citizen
    participant UI as Next.js UI
    participant API as FastAPI Backend
    participant AI as AI Agents
    participant DB as MongoDB
    participant Authority as Authority Team

    Citizen->>UI: Open Upload page
    Citizen->>UI: Enter issue details
    Citizen->>UI: Upload photo and optional voice note
    UI->>API: POST /api/complaints/report
    API->>AI: Transcribe voice and inspect photo
    AI->>AI: Classify issue and severity
    AI->>AI: Calculate trust score
    AI->>AI: Select department, official, SLA
    AI->>DB: Save complaint, evidence, classification, routing
    API-->>UI: Return complaint ID and assignment
    UI->>UI: Enable Generate PDF Report
    UI-->>Citizen: Show dashboard progress update
    API->>Authority: Notify assigned department
```

## AI Agent Pipeline

```mermaid
flowchart TD
    Input["Complaint Input"] --> Text["Text Description"]
    Input --> Photo["Photo Evidence"]
    Input --> Voice["Voice Note"]
    Input --> Location["Address + Latitude + Longitude + Ward + PIN"]

    Voice --> ASR["Speech-to-Text Agent"]
    Photo --> Vision["Image Understanding Agent"]
    Text --> Fusion["Multimodal Fusion"]
    ASR --> Fusion
    Vision --> Fusion
    Location --> Fusion

    Fusion --> Classification["Issue Classification"]
    Classification --> Severity["Severity Detection"]
    Severity --> Trust["Trust Score Verification"]
    Trust --> Router["Authority Routing Agent"]
    Router --> SLA["SLA Assignment"]
    SLA --> Save["Persist Complaint"]
    Save --> Dashboard["Citizen Dashboard Updates"]
    Save --> Analytics["Heatmap + Escalation Analytics"]
```

## Dashboard And Analytics Flow

```mermaid
flowchart LR
    Dashboard["Citizen Dashboard"] --> Reports["My Reports"]
    Dashboard --> TrustScore["AI Trust Score"]
    Dashboard --> Updates["AI Progress Updates"]
    Dashboard --> UploadCTA["Upload Report Button"]

    Reports --> ComplaintDetail["Complaint Details"]
    ComplaintDetail --> PDF["Generate PDF Report"]

    Heatmap["Heatmap Analytics"] --> Risk["Risk Distribution"]
    Heatmap --> Types["Incident Type Distribution"]
    Heatmap --> Time["Time Patterns"]
    Heatmap --> Clusters["Complaint Clusters"]

    Escalation["Escalation Page"] --> Pending["Pending Count"]
    Escalation --> Rate["Escalation Rate"]
    Escalation --> Overdue["Overdue Reports"]
```

## Backend API Map

```mermaid
flowchart TB
    FastAPI["FastAPI app.main"] --> AuthRouter["/api/auth"]
    FastAPI --> ComplaintsRouter["/api/complaints"]
    FastAPI --> HeatmapRouter["/api/heatmap"]
    FastAPI --> RoutesRouter["/api/routes"]
    FastAPI --> EscalationRouter["/api/escalation"]
    FastAPI --> Health["/health"]

    AuthRouter --> Login["JWT Login"]
    ComplaintsRouter --> Report["Submit Report"]
    ComplaintsRouter --> CitizenDash["Citizen Dashboard Data"]
    ComplaintsRouter --> Detail["Complaint Detail"]
    ComplaintsRouter --> Status["Status Update"]

    HeatmapRouter --> HeatmapData["Cluster Data"]
    HeatmapRouter --> RiskAnalytics["Risk Analytics"]
    HeatmapRouter --> IncidentAnalytics["Incident Type Analytics"]
    HeatmapRouter --> TimeAnalytics["Time Pattern Analytics"]

    RoutesRouter --> SaferPath["Safer Route Advisor"]
    EscalationRouter --> PendingAPI["Pending Count"]
    EscalationRouter --> RateAPI["Escalation Rate"]
```

## Deployment Flow

```mermaid
flowchart LR
    GitHub["GitHub Repository"] --> Render["Render Backend Service"]
    GitHub --> FrontendHost["Frontend Host"]

    Render --> BuildBackend["Install backend requirements"]
    BuildBackend --> StartBackend["uvicorn app.main:app --port $PORT"]
    StartBackend --> BackendURL["Backend Render URL"]

    FrontendHost --> Env["BACKEND_API_BASE_URL"]
    Env --> BackendURL

    Render --> MongoDB[("MongoDB Atlas")]
    Render --> NVIDIA["NVIDIA NIM API"]
```

## Core Data Flow

```mermaid
flowchart TD
    Submit["Citizen submits report"] --> Validate["Validate form + files"]
    Validate --> StoreMedia["Store uploaded media"]
    StoreMedia --> AIProcess["Run AI processing"]
    AIProcess --> Persist["Save complaint record"]
    Persist --> Assign["Assign authority and SLA"]
    Assign --> Notify["Send notifications if providers configured"]
    Persist --> Dashboard["Expose report in citizen dashboard"]
    Persist --> Heatmap["Expose geospatial analytics"]
    Persist --> Escalation["Monitor SLA and escalation status"]
```
