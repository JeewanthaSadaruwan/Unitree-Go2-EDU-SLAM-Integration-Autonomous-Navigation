# Navigation Configuration Guide

## 📍 Configuration File Location

Your Nav2 configuration is now in your workspace at:
**[src/go2_mapping/config/go2_nav2_params.yaml](src/go2_mapping/config/go2_nav2_params.yaml)**

This file contains ALL navigation parameters with detailed comments explaining each one.

## 🗺️ Key Components

### 1. **AMCL (Localization)**
Estimates where the robot is on the map.

**Key parameters:**
- `min_particles` / `max_particles` - More particles = better accuracy but slower
- `alpha1-5` - Odometry noise (increase if robot drifts)
- Laser model parameters - How to interpret scan data

### 2. **Costmaps** (Obstacle representation)

#### **Global Costmap** - For planning paths across entire map
- Uses static map from map_server
- `resolution: 0.05` - 5cm cells
- `inflation_radius: 0.55` - Safety buffer around obstacles (55cm)

#### **Local Costmap** - For obstacle avoidance
- Uses real-time sensor data (your LiDAR)
- `width: 3`, `height: 3` - 3x3 meter window around robot
- `update_frequency: 10.0` - Updates 10 times/second
- `rolling_window: true` - Moves with robot

**Important costmap topics to visualize in RViz:**
```bash
/global_costmap/costmap        # Global planning costmap
/local_costmap/costmap         # Local obstacle avoidance costmap
/local_costmap/published_footprint  # Robot footprint
```

### 3. **Controller** (Local trajectory execution)

Uses **DWB (Dynamic Window Approach)** planner.

**Velocity limits (adjust for Go2):**
```yaml
max_vel_x: 0.25          # Max forward speed (m/s)
max_vel_theta: 0.8       # Max rotation speed (rad/s)
acc_lim_x: 0.8           # Acceleration limit
```

**Trajectory critics** (scoring functions):
- `BaseObstacle` - Avoid hitting things
- `PathAlign` - Stay on the global path
- `GoalAlign` - Face the goal orientation
- `RotateToGoal` - Rotate before moving

### 4. **Planner** (Global path planning)

Uses **NavFn** (Dijkstra/A*) planner.

```yaml
use_astar: false         # Dijkstra is more thorough
allow_unknown: true      # Can plan through unexplored areas
tolerance: 0.5           # How close to get to goal
```

### 5. **Recovery Behaviors**

What to do when stuck:
- `spin` - Rotate in place to clear costmaps
- `backup` - Back up a bit
- `wait` - Wait for obstacles to clear

## 🎯 Common Tuning Scenarios

### Robot is too cautious / won't go through narrow spaces
```yaml
# In both global_costmap and local_costmap:
inflation_radius: 0.35          # Reduce from 0.55
cost_scaling_factor: 2.0        # Reduce from 3.0
```

### Robot moves too fast / unsafe
```yaml
# In controller_server -> FollowPath:
max_vel_x: 0.15                 # Reduce from 0.25
max_vel_theta: 0.5              # Reduce from 0.8
```

### Robot oscillates / wiggles
```yaml
# In controller_server -> FollowPath -> critics:
Oscillation.scale: 2.0          # Add this line
vtheta_samples: 10              # Reduce from 20
```

### Poor localization / robot jumps around map
```yaml
# In amcl:
max_particles: 3000             # Increase from 2000
alpha1: 0.3                     # Increase if wheels slip
alpha2: 0.3
```

### Robot gets stuck too easily
```yaml
# In controller_server -> progress_checker:
required_movement_radius: 0.3   # Reduce from 0.5
movement_time_allowance: 15.0   # Increase from 10.0
```

## 📊 Visualization in RViz

Add these topics to see what's happening:

```bash
# Costmaps
/global_costmap/costmap
/local_costmap/costmap

# Paths
/plan                          # Global path
/local_plan                    # Local trajectory

# Footprint
/local_costmap/published_footprint
/global_costmap/published_footprint

# Particles (localization)
/particle_cloud

# Goals
/goal_pose
```

## 🔧 Testing & Tuning Workflow

1. **Start navigation**
   ```bash
   ./start_bridge.sh              # Terminal 1
   ./start_navigation.sh          # Terminal 2
   ```

2. **Open RViz and visualize costmaps**
   ```bash
   rviz2
   ```

3. **Test navigation with simple goals**
   - Set initial pose
   - Send nearby goal first
   - Observe behavior

4. **Adjust parameters** in [go2_nav2_params.yaml](src/go2_mapping/config/go2_nav2_params.yaml)

5. **Restart navigation** to apply changes
   ```bash
   # Ctrl+C in navigation terminal, then:
   ./start_navigation.sh
   ```

6. **Repeat until satisfied**

## 📝 Parameter Quick Reference

| Component | File Section | What it does |
|-----------|-------------|--------------|
| Localization | `amcl` | Estimates robot pose |
| Global Planning | `planner_server` | Computes full path to goal |
| Local Control | `controller_server` | Executes path, avoids obstacles |
| Global Map | `global_costmap` | Map for planning |
| Local Map | `local_costmap` | Sensor data for avoidance |
| Recovery | `recoveries_server` | What to do when stuck |
| Behavior Tree | `bt_navigator` | Orchestrates everything |

## 🚨 Common Issues

### "Waiting for map to be published"
- Check map_server is running and active
- Verify map file path in config

### "No path could be found"
- Inflation might be too high
- Start or goal in obstacle
- Check `allow_unknown` parameter

### Robot doesn't move
- Check `/cmd_vel` topic: `ros2 topic echo /cmd_vel`
- Verify bridge is running
- Check velocity limits aren't too restrictive

### AMCL not converging
- Set initial pose in RViz
- Drive robot around to help particles converge
- Increase `max_particles`

## 📚 Further Reading

- [Nav2 Documentation](https://navigation.ros.org/)
- [DWB Controller](https://navigation.ros.org/configuration/packages/configuring-dwb-controller.html)
- [Costmap 2D](https://navigation.ros.org/configuration/packages/configuring-costmaps.html)
- [AMCL](https://navigation.ros.org/configuration/packages/configuring-amcl.html)

---

**Pro Tip:** Always visualize costmaps in RViz when tuning. They show you exactly what the robot "sees" and why it makes certain decisions!
