# AD-CUBE-001 — CubeSpace XVI Sovereign Personal Operating System

**Status:** APPROVED ARCHITECTURE CORRECTION  
**Effective:** Immediate  
**Supersedes:** Cube = client container  
**Replaces with:** Cube = sovereign personal operating system

## Decision

CubeSpace XVI is the sovereign personal workroom, workstation and operating system. A Cube contains its own content, memory, intelligence, coordination, validation, secrets, communication and multitasking capabilities.

ERP and future applications are governed products built, tested and operated under the Cube. The Cube is not ERP.

## Cube components

| Component | Responsibility |
|---|---|
| INNM-WOSDS | Primary intelligence layer: knowledge processing, reasoning, research, learning, domain intelligence and memory use. |
| TaskMaster | Central coordination authority: planning, decomposition, assignment, coordination, outside-Cube authority, acceptance and escalation. |
| VALIDATER | Independent assurance authority: verification, security, regression, policy, risk and rejection of deficient work. |
| Keybox | Secret authority: API keys, credentials, tokens, rotation and audit. Agents never own raw secrets. |
| C-Junction | Controlled communication: request, response, schema, authority, provenance and cross-system validation. TaskMaster authorizes communication. |
| Multitasker | Execution and queue manager: parallel work, dependencies, priority, resources and completion routing. |
| Cube content/memory | Files, knowledge, procedures, decisions, artifacts and history belonging to the Cube. |

## Authority rules

1. No subsystem communicates externally without TaskMaster authorization.
2. TaskMaster is the only component with governed outside-Cube connection and outside-Cube memory access.
3. C-Junction validates communication; it does not independently authorize external communication.
4. VALIDATER is independent and may reject work.
5. Keybox releases the minimum required secret under policy; raw secrets do not enter ordinary prompts or content.
6. Multitasker executes multiple tasks under TaskMaster ownership, priority and resource controls.
7. Internal components cannot bypass TaskMaster, VALIDATER, Keybox or C-Junction controls.

## Standard flow

TaskMaster receives and decomposes the task → INNM-WOSDS reasons over authorized Cube content → Multitasker executes permitted work → Keybox releases controlled secrets where required → C-Junction validates outbound request → external response returns through TaskMaster → C-Junction validates inbound response → VALIDATER independently checks the result → TaskMaster records evidence and accepts, rejects, revises or escalates.

## Repository alignment

- **ZQ_CubeSpaceXVI:** Cube OS architecture, sovereignty and governance.
- **ZQ_Taskbox:** TaskMaster workstation and operational console.
- **P1:** governance runtime, validation, evidence, ownership, fencing and acceptance.
- **ZQ_Autoser_OS-Xv1:** execution methods, workflow engines, connectors and operational behaviour.
- **ZQ_XV1_CLOUD_ERP:** separate customer ERP product and ERP runtime.

## ERP isolation

The Cube builds, governs, validates and stores evidence for ERP. ERP remains a separate product.

ERP customers see only the ERP application, its features, data, roles and approved workflows. They do not see INNM-WOSDS, TaskMaster, VALIDATER, Keybox, C-Junction, Multitasker, Cube governance, internal memory or other Cubes.

## First unified integration test

Prove with synthetic data that one Cube can:

1. receive a TaskMaster task;
2. assign INNM-WOSDS work;
3. execute multiple activities through Multitasker;
4. obtain a controlled test credential from Keybox;
5. validate outbound and inbound exchange through C-Junction;
6. have VALIDATER reject an intentional error;
7. record evidence through TaskMaster; and
8. demonstrate no secret, validator, external-connection or TaskMaster bypass.

This decision defines architecture only. Implementation, verification, deployment environment, deployment outcome and production authorization remain separate states.
