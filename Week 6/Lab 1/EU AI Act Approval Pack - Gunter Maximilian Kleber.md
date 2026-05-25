# EU AI Act Approval Pack - Gunter Maximilian Kleber

## Executive Summary

This approval pack evaluates four different AI use cases under the EU AI Act framework. The objective is to classify each system according to its legal risk level, assess the proposed AI architecture, identify provider and deployer responsibilities, and determine whether the system can be approved for deployment.

The reviewed scenarios include one prohibited AI practice, one high-risk AI system, one transparency-based limited-risk system, and one minimal-risk AI use case. Each case was analyzed from a practical consulting perspective with focus on operational deployment, human oversight, affected persons, and compliance implications.

The final recommendation varies between full approval, approval with controls, and denial with redesign depending on the identified risk level and the legal obligations triggered by the system.

---

# Case 1

## Client Brief

A retail company wants to install AI powered cameras in shopping malls to identify emotionally vulnerable customers and dynamically push highly personalized advertising on nearby digital displays. The system would analyze facial expressions, stress indicators, and estimated emotional states in real time to maximize purchasing behavior. No explicit consent from customers is planned. The company expects the system to improve conversion rates and impulse purchases.

## Likely Category

Prohibited AI Practice

## Why

The proposed system uses biometric and emotional analysis in a manipulative commercial context without meaningful consent. The system attempts to exploit emotional vulnerability and behavioral manipulation in public spaces.

## Proposed AI Architecture

- Camera system captures live customer video streams
- AI model performs facial and emotional analysis
- Customer emotional state is classified in real time
- Advertising engine changes content dynamically
- No meaningful human review before intervention

## Provider / Deployer / Vendor

- Provider: AI emotion recognition software company
- Deployer: Retail company operating the malls
- Vendor: Camera and infrastructure providers

## Required Obligations or Controls

The system cannot be approved under the EU AI Act in its current form because the core functionality itself falls into prohibited territory.

## Decision

Deny and redesign

## Lawful Redesign Option

Replace emotional manipulation with anonymous customer flow analytics and opt-in recommendation systems without biometric profiling or emotional inference.

---

# Case 2

## Client Brief

A financial institution plans to deploy an AI system to support loan approval decisions for private customers. The model evaluates income, spending behavior, account history, debt exposure, and additional behavioral scoring signals to estimate creditworthiness. Human employees review borderline cases but most applications are automatically processed through the AI recommendation system.

## Likely Category

High-risk AI System

## Why

Creditworthiness assessments directly affect access to essential financial services and fall under Annex III high-risk use cases.

## Proposed AI Architecture

- Customer submits digital application
- Structured financial and behavioral data is collected
- AI scoring model evaluates default probability
- Risk score and recommendation are generated
- Human reviewer validates unclear or critical decisions
- Audit logs and decision records are stored

## Provider / Deployer / Vendor

- Provider: Internal AI development team or external scoring vendor
- Deployer: Financial institution
- Vendor: Data infrastructure and cloud providers

## Required Obligations or Controls

- Human oversight
- Risk management process
- Logging and traceability
- Data governance and quality validation
- Transparency toward affected customers
- Monitoring for discrimination and bias

## Decision

Approve with controls

---

# Case 3

## Client Brief

A customer service provider wants to launch an AI chatbot on its website to answer support requests, summarize problems, and guide users through troubleshooting steps before escalation to a human employee. The chatbot clearly identifies itself as an AI assistant and allows users to request human support at any time.

## Likely Category

Limited Risk with Transparency Obligations

## Why

The system mainly triggers transparency obligations because users interact directly with an AI system and must be informed accordingly.

## Proposed AI Architecture

- Customer opens support chat
- AI assistant processes user questions
- Suggested troubleshooting steps are generated
- Human escalation option remains available
- Conversation logs are stored for quality improvement

## Provider / Deployer / Vendor

- Provider: Chatbot platform vendor
- Deployer: Customer service company
- Vendor: LLM API provider

## Required Obligations or Controls

- Clear disclosure that users interact with AI
- Escalation path to humans
- Safe prompt handling and moderation
- GDPR compliant storage and processing

## Decision

Approve with controls

---

# Case 4

## Client Brief

A marketing agency uses generative AI tools internally to create first draft social media captions and brainstorming ideas for creative campaigns. Final content is always reviewed, edited, and approved by human employees before publication.

## Likely Category

Minimal Risk

## Why

The system supports internal productivity tasks without directly affecting rights, safety, or access to essential services.

## Proposed AI Architecture

- Marketing employee enters campaign brief
- Generative AI produces draft content ideas
- Human employee reviews and edits output
- Final publication remains fully human controlled

## Provider / Deployer / Vendor

- Provider: Generative AI platform provider
- Deployer: Marketing agency
- Vendor: Cloud infrastructure providers

## Required Obligations or Controls

No specific AI Act obligations beyond general compliance expectations. Standard GDPR and copyright considerations still apply.

## Decision

Approve

---

# Closing Note

After comparing the intended categories with the consultant assessment, the classifications largely aligned with the expected AI Act treatment. The prohibited and high-risk scenarios were relatively easy to identify because they directly affected vulnerable individuals or access to essential services. The limited-risk and minimal-risk examples required more careful analysis because both used generative AI but differed significantly in operational impact and transparency requirements.

The exercise showed how important deployment context, affected persons, and human oversight are when evaluating AI systems under the EU AI Act.