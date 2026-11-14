import os

app_js_path = r'D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js'
with open(app_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace elephantLocomotionController with refined version
old_ctrl_start = '  const elephantLocomotionController = {'
old_ctrl_end = '  function buildArticulatedElephantModel() {'

idx_start = content.find(old_ctrl_start)
idx_end = content.find(old_ctrl_end)
assert idx_start != -1 and idx_end != -1, "Could not find elephantLocomotionController block"

refined_controller = '''  const elephantLocomotionController = {
    modelForwardAxis: new THREE.Vector3(1, 0, 0), // Intrinsic model forward axis (+X verified from GLB anatomy)
    lastValidDirection: new THREE.Vector3(1, 0, 0),
    targetDirection: new THREE.Vector3(1, 0, 0),
    currentQuaternion: new THREE.Quaternion(),
    targetQuaternion: new THREE.Quaternion(),
    lastPosition: null,
    lastSimTime: null,
    isStationary: false,

    reset(initialPos, initialVel) {
      if (initialVel && Math.hypot(initialVel.vx || 0, initialVel.vy || 0) > 0.05) {
        this.lastValidDirection.set(initialVel.vx, 0, initialVel.vy).normalize();
      } else {
        this.lastValidDirection.set(1, 0, 0);
      }
      this.targetDirection.copy(this.lastValidDirection);
      this.targetQuaternion.setFromUnitVectors(this.modelForwardAxis, this.targetDirection);
      this.currentQuaternion.copy(this.targetQuaternion);
      this.lastSimTime = 0.0;
      if (initialPos) {
        this.lastPosition = new THREE.Vector3(initialPos.x, initialPos.y, initialPos.z);
      }
      if (threeObjects.elephantGroup) {
        threeObjects.elephantGroup.quaternion.copy(this.currentQuaternion);
      }
      elephantLastValidHeading = Math.atan2(-this.lastValidDirection.z, this.lastValidDirection.x);
    },

    update(group, posX, posY, posZ, vx, vy, isPlaying, simTime = 0.0, delta = 0.033) {
      // 1. Simulation world position update (strictly separated)
      group.position.set(posX, posY, posZ);

      // 2. Determine intended horizontal movement direction
      const speed = Math.hypot(vx, vy);
      let moveDir = null;
      if (speed > 0.05) {
        moveDir = new THREE.Vector3(vx, 0, vy).normalize();
      } else if (this.lastPosition) {
        const dX = posX - this.lastPosition.x;
        const dZ = posZ - this.lastPosition.z;
        if (Math.hypot(dX, dZ) > 0.02) {
          moveDir = new THREE.Vector3(dX, 0, dZ).normalize();
        }
      }

      if (moveDir && moveDir.lengthSq() > 0.5) {
        this.isStationary = false;
        this.lastValidDirection.copy(moveDir);
        this.targetDirection.copy(moveDir);
        this.targetQuaternion.setFromUnitVectors(this.modelForwardAxis, this.targetDirection);
      } else {
        // Temporary stop: preserve last valid heading exactly (no flipping/turning)
        this.isStationary = true;
        this.targetQuaternion.setFromUnitVectors(this.modelForwardAxis, this.lastValidDirection);
      }

      // 3. Smooth shortest-arc spherical linear interpolation (Quaternion SLERP)
      // When seeking/scrubbing or time jumps (>0.25s), snap immediately (slerpFactor = 1.0)
      // During continuous forward playback, smoothly interpolate at natural turn rate
      const isContinuousPlayback = isPlaying && this.lastSimTime !== null && Math.abs(simTime - this.lastSimTime) < 0.25;
      const slerpFactor = isContinuousPlayback ? Math.min(1.0, (delta || 0.033) * 8.0) : 1.0;
      this.currentQuaternion.slerp(this.targetQuaternion, slerpFactor);
      group.quaternion.copy(this.currentQuaternion);

      // Sync legacy scalar heading for HUD telemetry and secondary trackers
      elephantLastValidHeading = Math.atan2(-this.lastValidDirection.z, this.lastValidDirection.x);

      // 4. Update history
      this.lastSimTime = simTime;
      if (!this.lastPosition) {
        this.lastPosition = new THREE.Vector3(posX, posY, posZ);
      } else {
        this.lastPosition.set(posX, posY, posZ);
      }

      // 5. Diagnostic instrumentation overlay / debug telemetry hook
      const fwdWorld = this.modelForwardAxis.clone().applyQuaternion(this.currentQuaternion);
      let dotProduct = 0;
      if (moveDir) {
        dotProduct = fwdWorld.dot(moveDir);
      } else {
        dotProduct = fwdWorld.dot(this.lastValidDirection);
      }
      window.__PRW_ELEPHANT_LOCOMOTION_DEBUG__ = {
        worldPosition: { x: posX, y: posY, z: posZ },
        velocity: { vx, vy },
        speed: speed,
        isStationary: this.isStationary,
        targetDirection: { x: this.targetDirection.x, z: this.targetDirection.z },
        modelForwardWorld: { x: fwdWorld.x, y: fwdWorld.y, z: fwdWorld.z },
        dotProductWithVelocity: dotProduct,
        quaternion: { x: this.currentQuaternion.x, y: this.currentQuaternion.y, z: this.currentQuaternion.z, w: this.currentQuaternion.w },
        headingRad: elephantLastValidHeading
      };
    }
  };
'''

content = content[:idx_start] + refined_controller + '\n' + content[idx_end:]

# In syncThreeScene, ensure simTime (t) is passed
old_call = '''      elephantLocomotionController.update(
        threeObjects.elephantGroup,
        animal.x,
        terrY,
        animal.y,
        animal.vx,
        animal.vy,
        isPlaying,
        deltaT
      );'''

new_call = '''      elephantLocomotionController.update(
        threeObjects.elephantGroup,
        animal.x,
        terrY,
        animal.y,
        animal.vx,
        animal.vy,
        isPlaying,
        t,
        deltaT
      );'''

if old_call in content:
    content = content.replace(old_call, new_call, 1)
else:
    old_call_crlf = old_call.replace('\n', '\r\n')
    if old_call_crlf in content:
        content = content.replace(old_call_crlf, new_call.replace('\n', '\r\n'), 1)

# In runSimulation, export window.simulationData
old_assign = 'simulationData = data;'
new_assign = 'simulationData = data;\n      window.simulationData = data;'
if 'window.simulationData = data;' not in content:
    content = content.replace(old_assign, new_assign, 1)

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Refined AnimalLocomotionController applied to app.js!")

