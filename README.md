# 🌙 LunaBot

## Risk-Aware Autonomous Navigation and Habitat Monitoring Robot for Lunar Habitats using ROS 2

LunaBot is a ROS 2-based autonomous robotic system designed to support future lunar habitats through **autonomous navigation, environmental monitoring, risk-aware mission prioritization, perception, and operator supervision**.

Instead of functioning only as a robot that follows predefined patrol points, LunaBot introduces a **risk-aware mission layer** that allows habitat conditions to influence where the robot should go next.

---

## 🚀 Problem Statement

Future lunar missions aim toward sustained human presence on the Moon.

Maintaining such habitats requires continuous inspection of environmental conditions and infrastructure. However, lunar environments introduce several challenges:

- No GPS availability
- Constrained indoor habitat spaces
- Difficult outdoor terrain
- Obstacles and navigation hazards
- Limited astronaut time
- Need for continuous environmental monitoring
- Requirement for reliable autonomous operation

LunaBot is designed as a robotic support platform capable of autonomously navigating a lunar habitat while monitoring its condition and assisting with routine patrol operations.

---

## 💡 Our Solution

LunaBot combines:

- ROS 2-based modular robotics architecture
- Autonomous navigation
- Obstacle-aware path planning
- Habitat environmental monitoring
- Risk-aware mission prioritization
- Camera-based monitoring
- Operator dashboard
- Routine autonomous patrol
- Alert generation

The overall mission cycle is:

```text
MONITOR
   ↓
EVALUATE RISK
   ↓
PRIORITIZE
   ↓
NAVIGATE
   ↓
INSPECT
   ↓
REPORT
   ↓
REPEAT
```

---

# 🧠 Key Innovation — Risk-Aware Autonomous Patrol

Traditional autonomous navigation primarily answers:

> **How should the robot reach its destination?**

LunaBot adds another level of intelligence:

> **Which destination requires the robot's attention first?**

Environmental conditions such as temperature and oxygen level can be combined with habitat-zone importance to influence mission priority.

This connects:

```text
Environmental Monitoring
          +
     Risk Assessment
          +
  Mission Prioritization
          +
 Autonomous Navigation
```

As a result, LunaBot can move toward **condition-driven patrol** rather than relying only on a fixed waypoint sequence.

---

# 🏗️ System Architecture

```text
                ┌─────────────────────┐
                │    Operator UI      │
                │ Status & Controls   │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Mission Manager   │
                │   Risk Evaluation   │
                └──────────┬──────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
     Navigation      Habitat Monitor    Perception
     & Planning       Temp / O2       Camera/Sensors
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                    ROS 2 Middleware
                           │
                           ▼
                  Robot / Simulation
```

Detailed architecture:

`docs/architecture.md`

---

# ⚙️ Core Components

## Autonomous Navigation

Responsible for:

- Goal-directed movement
- Path planning
- Localization
- Obstacle detection
- Obstacle-aware navigation
- Autonomous patrol movement

## Habitat Monitoring

Processes environmental information such as:

- Temperature
- Oxygen level
- Habitat-zone condition
- Environmental warnings
- Zone criticality

## Mission Manager

Connects habitat monitoring with robot autonomy.

It determines **where LunaBot should direct its attention** based on environmental conditions and mission priority.

## Perception

Provides environmental awareness through camera and sensor information.

The architecture can support:

- Camera
- LiDAR
- IMU
- Odometry

## Operator Interface

Provides human operators with access to:

- Robot status
- Mission status
- Environmental readings
- Risk information
- Camera monitoring
- Alerts
- Robot controls

---

# 🔄 Mission Workflow

```text
Habitat / Sensor Data
        ↓
Environmental Monitoring
        ↓
Risk Evaluation
        ↓
Mission Prioritization
        ↓
Target Selection
        ↓
Autonomous Navigation
        ↓
Obstacle Avoidance
        ↓
Zone Inspection
        ↓
Dashboard / Alert
        ↓
Continue Mission
```

---

# 🌡️ Example Risk-Aware Scenario

Consider four habitat zones:

```text
Zone A : Normal
Zone B : Normal
Zone C : Abnormal O2
Zone D : Normal
```

A conventional fixed patrol may continue:

```text
A → B → C → D
```

LunaBot can prioritize the abnormal zone:

```text
O2 Anomaly
    ↓
Risk Increase
    ↓
Zone C Prioritized
    ↓
Navigation Goal
    ↓
Inspection
    ↓
Alert / Report
```

This allows robot behaviour to respond to the **state of the habitat**.

---

# 🛠️ Technology Stack

- ROS 2
- Python
- Robot simulation
- Autonomous navigation
- Camera/perception pipeline
- Environmental monitoring
- Git
- GitHub

---

# 📁 Repository Structure

```text
LunaBot/
│
├── README.md
├── LICENSE
├── .gitignore
│
├── lunabot_core/
│   └── ROS 2 application source
│
├── docs/
│   ├── architecture.md
│   ├── innovation.md
│   └── roadmap.md
│
└── media/
    ├── screenshots/
    └── demo/
```

---

# 📚 Documentation

### System Architecture

`docs/architecture.md`

Explains LunaBot's modules, ROS 2 architecture, mission workflow and system design.

### Innovation

`docs/innovation.md`

Explains the risk-aware autonomous patrol concept and how habitat conditions influence robot missions.

### Development Roadmap

`docs/roadmap.md`

Documents the prototype development stages and future expansion toward autonomous lunar habitat support.

---

# 🌕 Why LunaBot?

Sustained lunar exploration will require more than transporting astronauts to the Moon.

Habitats must be continuously:

- Monitored
- Inspected
- Protected
- Maintained

Routine inspection should not consume valuable astronaut time.

LunaBot explores how autonomous robotics can combine **mobility, environmental awareness and mission-level intelligence** to support future lunar crews.

---

# 🔭 Future Scope

Future LunaBot versions can incorporate:

- Physical LiDAR, camera and IMU
- Pressure monitoring
- Radiation monitoring
- Smoke and gas detection
- Predictive anomaly detection
- Predictive maintenance
- Energy-aware path planning
- Autonomous charging
- Robotic manipulation
- Multi-robot coordination

---

# 🎯 Project Goal

The goal of LunaBot is to demonstrate a prototype where a robot can:

1. Monitor a lunar habitat
2. Identify conditions requiring attention
3. Prioritize mission targets
4. Navigate autonomously
5. Avoid obstacles
6. Inspect the selected area
7. Communicate mission information to human operators

---

# 👥 Team

**SpaceWalkers**

A four-member team working across:

- System design, research and project leadership
- ROS 2 software, autonomy and frontend development
- Hardware and electronics
- Integration, testing and support

---

# 🌙 Vision

LunaBot is designed not merely as an autonomous mobile robot, but as the foundation of an **autonomous robotic habitat-support system**.

> **LunaBot — Autonomous eyes and wheels for the habitats beyond Earth.**
