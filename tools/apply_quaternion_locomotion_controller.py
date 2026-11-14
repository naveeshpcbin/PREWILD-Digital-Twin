import os

app_js_path = r'D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js'
with open(app_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Define the dedicated Animal Locomotion & Orientation Controller
controller_code = '''
  // ==========================================================================
  // Dedicated Animal Locomotion & Orientation Controller (Robust Separation)
  // ==========================================================================
  const elephantLocomotionController = {
    modelForwardAxis: new THREE.Vector3(1, 0, 0), // Intrinsic model forward axis (+X verified from GLB anatomy)
    lastValidDirection: new THREE.Vector3(1, 0, 0),
    targetDirection: new THREE.Vector3(1, 0, 0),
    currentQuaternion: new THREE.Quaternion(),
    targetQuaternion: new THREE.Quaternion(),
    lastPosition: null,
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
      if (initialPos) {
        this.lastPosition = new THREE.Vector3(initialPos.x, initialPos.y, initialPos.z);
      }
      if (threeObjects.elephantGroup) {
        threeObjects.elephantGroup.quaternion.copy(this.currentQuaternion);
      }
      elephantLastValidHeading = Math.atan2(-this.lastValidDirection.z, this.lastValidDirection.x);
    },

    update(group, posX, posY, posZ, vx, vy, isPlaying, delta = 0.033) {
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
      const slerpFactor = isPlaying ? Math.min(1.0, (delta || 0.033) * 8.0) : 1.0;
      this.currentQuaternion.slerp(this.targetQuaternion, slerpFactor);
      group.quaternion.copy(this.currentQuaternion);

      // Sync legacy scalar heading for HUD telemetry and secondary trackers
      elephantLastValidHeading = Math.atan2(-this.lastValidDirection.z, this.lastValidDirection.x);

      // 4. Update position history
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

# Place controller right before buildArticulatedElephantModel
anchor = '  function buildArticulatedElephantModel() {'
assert anchor in content, "Could not find buildArticulatedElephantModel"
if 'const elephantLocomotionController =' not in content:
    content = content.replace(anchor, controller_code + '\n' + anchor, 1)

# Fix fallback position heave in animateThree
target_heave = 'threeObjects.elephantGroup.position.y = Math.abs(Math.sin(walkCycle * 2)) * 0.12;'
replace_heave = 'if (threeObjects.elephantFallbackGroup) threeObjects.elephantFallbackGroup.position.y = Math.abs(Math.sin(walkCycle * 2)) * 0.12;'
if target_heave in content:
    content = content.replace(target_heave, replace_heave, 1)

# In syncThreeScene, wire up elephantLocomotionController.update
old_sync_heading = '''    // 1. Elephant Position, Ground Elevation & True Forward Heading
    const animal = getGroundTruthAtTime(t);
    if (animal && threeObjects.elephantGroup) {
      const terrY = getTerrainElevation(animal.x, animal.y);
      threeObjects.elephantGroup.position.set(animal.x, terrY, animal.y);

      const speed = Math.hypot(animal.vx, animal.vy);
      if (speed > 0.05) {
        // True forward heading: for model facing standard -Z, forward heading is Math.atan2(-vx, -vy)
        const targetHeading = Math.atan2(-animal.vy, animal.vx);
        let diff = targetHeading - elephantLastValidHeading;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;
        const lerpFactor = isPlaying ? 0.35 : 1.0;
        elephantLastValidHeading += diff * lerpFactor;
        threeObjects.elephantGroup.rotation.y = elephantLastValidHeading;
      } else {
        threeObjects.elephantGroup.rotation.y = elephantLastValidHeading;
      }'''

new_sync_heading = '''    // 1. Elephant Position, Ground Elevation & True Forward Heading
    const animal = getGroundTruthAtTime(t);
    if (animal && threeObjects.elephantGroup) {
      const terrY = getTerrainElevation(animal.x, animal.y);
      const deltaT = threeClock ? Math.min(threeClock.getDelta(), 0.1) : 0.033;
      elephantLocomotionController.update(
        threeObjects.elephantGroup,
        animal.x,
        terrY,
        animal.y,
        animal.vx,
        animal.vy,
        isPlaying,
        deltaT
      );
      const speed = Math.hypot(animal.vx, animal.vy);'''

if old_sync_heading in content:
    content = content.replace(old_sync_heading, new_sync_heading, 1)
else:
    old_sync_heading_crlf = old_sync_heading.replace('\n', '\r\n')
    assert old_sync_heading_crlf in content, "Could not find old_sync_heading in content"
    content = content.replace(old_sync_heading_crlf, new_sync_heading.replace('\n', '\r\n'), 1)

# In runSimulation reset
old_run_reset = '''      currentTime = 0.0;
      const initialAnimal = getGroundTruthAtTime(0);
      if (initialAnimal && Math.hypot(initialAnimal.vx, initialAnimal.vy) > 0.05) {
        elephantLastValidHeading = Math.atan2(-initialAnimal.vy, initialAnimal.vx);
      } else {
        elephantLastValidHeading = 0.0;
      }
      if (threeObjects.elephantGroup) {
        threeObjects.elephantGroup.rotation.y = elephantLastValidHeading;
      }'''

new_run_reset = '''      currentTime = 0.0;
      const initialAnimal = getGroundTruthAtTime(0);
      if (initialAnimal) {
        const initTerrY = getTerrainElevation(initialAnimal.x, initialAnimal.y);
        elephantLocomotionController.reset(
          new THREE.Vector3(initialAnimal.x, initTerrY, initialAnimal.y),
          initialAnimal
        );
      }'''

if old_run_reset in content:
    content = content.replace(old_run_reset, new_run_reset, 1)
else:
    old_run_reset_crlf = old_run_reset.replace('\n', '\r\n')
    assert old_run_reset_crlf in content, "Could not find old_run_reset in content"
    content = content.replace(old_run_reset_crlf, new_run_reset.replace('\n', '\r\n'), 1)

# In btnReset click handler
old_btn_reset = '''    currentTime = 0;
    const initialAnimal = getGroundTruthAtTime(0);
    if (initialAnimal && Math.hypot(initialAnimal.vx, initialAnimal.vy) > 0.05) {
      elephantLastValidHeading = Math.atan2(-initialAnimal.vy, initialAnimal.vx);
    } else {
      elephantLastValidHeading = 0.0;
    }
    if (threeObjects.elephantGroup) {
      threeObjects.elephantGroup.rotation.y = elephantLastValidHeading;
    }'''

new_btn_reset = '''    currentTime = 0;
    const initialAnimal = getGroundTruthAtTime(0);
    if (initialAnimal) {
      const initTerrY = getTerrainElevation(initialAnimal.x, initialAnimal.y);
      elephantLocomotionController.reset(
        new THREE.Vector3(initialAnimal.x, initTerrY, initialAnimal.y),
        initialAnimal
      );
    }'''

if old_btn_reset in content:
    content = content.replace(old_btn_reset, new_btn_reset, 1)
else:
    old_btn_reset_crlf = old_btn_reset.replace('\n', '\r\n')
    assert old_btn_reset_crlf in content, "Could not find old_btn_reset in content"
    content = content.replace(old_btn_reset_crlf, new_btn_reset.replace('\n', '\r\n'), 1)

# Export controller to window
export_target = 'window.setCameraView = setCameraView;'
if 'window.elephantLocomotionController =' not in content:
    content = content.replace(export_target, export_target + '\n  window.elephantLocomotionController = elephantLocomotionController;')

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: AnimalLocomotionController integrated into app.js!")
