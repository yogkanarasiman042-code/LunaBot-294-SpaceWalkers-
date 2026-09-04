# LunaBot System Architecture

## 1. Overview

LunaBot is a ROS 2-based autonomous robotic system designed for autonomous navigation, habitat monitoring, risk-aware patrol, and routine inspection operations inside simulated lunar habitat environments.

The system follows a modular architecture in which navigation, perception, environmental monitoring, mission management, and the operator interface function as separate components while communicating through ROS 2.

The architecture focuses on three major objectives:

- Autonomous and safe navigation
- Continuous habitat condition monitoring
- Risk-aware mission decision making

---

## 2. High-Level Architecture

```text
                ┌─────────────────────────┐
                │      LunaBot UI         │
                │ Monitoring & Controls   │
                └────────────┬────────────┘
                             │
                             ▼
                ┌─────────────────────────┐
                │    Mission Manager      │
                │    Risk Evaluation      │
                └────────────┬────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
 ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
 │   Navigation   │ │ Habitat Monitor│ │   Perception   │
 │   & Planning   │ │ Temp / O2 etc. │ │ Camera/Sensors │
 └───────┬────────┘ └───────┬────────┘ └───────┬────────┘
         │                   │                  │
         └───────────────────┼──────────────────┘
                             ▼
                 ┌──────────────────────┐
                 │   ROS 2 Middleware   │
                 │ Topics / Nodes / TF  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Robot / Simulation   │
                 │ Lunar Habitat World  │
                 └──────────────────────┘
```

---

## 3. Core Modules

### 3.1 Mission Management

The mission-management layer coordinates LunaBot's autonomous patrol behaviour.

Instead of treating every location in the habitat with equal priority, environmental conditions and zone importance can be evaluated before selecting the robot's next mission target.

This forms the basis of LunaBot's **risk-aware autonomous patrol system**.

---

### 3.2 Autonomous Navigation

The navigation layer is responsible for moving LunaBot safely between mission targets.

It handles functions such as:

- Goal-directed autonomous movement
- Path planning
- Localization
- Obstacle detection
- Obstacle-aware navigation
- Movement between habitat zones

The mission manager determines **where the robot should go**, while the navigation system determines **how the robot should safely reach that destination**.

---

### 3.3 Habitat Monitoring

The habitat-monitoring module processes environmental information from different sections of the lunar habitat.

Parameters can include:

- Temperature
- Oxygen level
- Habitat-zone condition
- Environmental warnings
- Zone criticality

Abnormal environmental conditions can trigger alerts and influence mission priority.

---

### 3.4 Risk-Aware Mission Layer

A major architectural feature of LunaBot is the separation between navigation intelligence and mission intelligence.

A conventional autonomous navigation system primarily answers:

> **How can the robot reach the selected destination safely?**

LunaBot additionally considers:

> **Which destination requires the robot's attention first?**

Environmental information and the operational importance of habitat zones can therefore influence the next patrol target.

This allows the patrol system to become **condition-driven rather than purely waypoint-driven**.

---

### 3.5 Perception

The perception layer provides information about the robot's surroundings.

The LunaBot architecture supports sensor information from components such as:

- Camera
- LiDAR
- IMU
- Odometry

These sources provide the foundation for obstacle detection, localization, environmental awareness, and future sensor-fusion improvements.

---

### 3.6 Operator Interface

The LunaBot operator interface provides a human-readable representation of the robot's operation.

The interface can present:

- Robot status
- Mission status
- Current patrol target
- Environmental readings
- Risk information
- Camera monitoring
- Alerts
- Navigation information
- Operator controls

This allows astronauts or habitat operators to supervise LunaBot without continuously controlling its movement.

---

## 4. ROS 2 Communication Architecture

ROS 2 acts as the communication backbone of LunaBot.

Independent components can exchange information through ROS 2 nodes, topics, messages, and transforms.

This modular architecture provides:

- Independent component development
- Easier debugging
- Expandability
- Separation of responsibilities
- Simulation integration
- Future hardware integration

---

## 5. Mission Decision Flow

```text
Environmental / Sensor Data
            │
            ▼
     Habitat Monitoring
            │
            ▼
       Risk Evaluation
            │
            ▼
    Mission Prioritization
            │
            ▼
       Target Selection
            │
            ▼
    Autonomous Navigation
            │
            ▼
     Obstacle Avoidance
            │
            ▼
      Zone Inspection
            │
            ▼
    Status / Alert Update
            │
            ▼
       Continue Patrol
```

---

## 6. Risk-Aware Patrol Concept

Consider a habitat containing several zones:

```text
Zone A ─ Normal
Zone B ─ Normal
Zone C ─ Abnormal Oxygen Level
Zone D ─ Normal
```

A fixed patrol robot may continue:

```text
A → B → C → D
```

LunaBot's mission layer can instead identify that **Zone C requires higher attention** and prioritize the appropriate mission target.

The navigation system can then calculate and execute the movement required to reach that target safely.

Therefore, LunaBot combines:

```text
Habitat Awareness
        +
Risk Assessment
        +
Mission Decision
        +
Autonomous Navigation
```

rather than treating navigation and habitat monitoring as unrelated functions.

---

## 7. Complete System Workflow

```text
        Habitat Environment
                │
                ▼
        Sensors / Monitoring
                │
                ▼
       Environmental Analysis
                │
                ▼
          Risk Assessment
                │
                ▼
          Mission Manager
                │
                ▼
         Priority Selection
                │
                ▼
       Navigation / Planning
                │
                ▼
       Obstacle-Aware Motion
                │
                ▼
         Habitat Inspection
                │
                ▼
       Dashboard + Alerts
                │
                ▼
          Mission Continues
```

---

## 8. Modular Design Philosophy

LunaBot is designed as a modular robotic platform.

Navigation, monitoring, perception, mission logic, and visualization are separated so that individual components can be improved without redesigning the complete system.

Simulation components can later be replaced or extended using physical hardware such as:

- LiDAR sensors
- Cameras
- IMU
- Temperature sensors
- Oxygen sensors
- Pressure sensors
- Radiation sensors

This makes the architecture suitable for progressive development from a simulation prototype toward a physical robotic platform.

---

## 9. System Objective

The objective of LunaBot is not merely to create a robot that moves autonomously.

The system aims to combine:

**Mobility + Environmental Awareness + Risk Assessment + Mission Intelligence**

to create an autonomous robotic assistant capable of supporting continuous inspection and monitoring of future lunar habitats.
