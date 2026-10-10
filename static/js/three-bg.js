
(function () {
  const canvas = document.getElementById("hero-canvas");
  if (!canvas || typeof THREE === "undefined") return;

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
  camera.position.set(0, 0.4, 7.2);

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  function sizeRenderer() {
    const rect = canvas.parentElement.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height, 1);
    renderer.setSize(size, size, false);
    camera.aspect = 1;
    camera.updateProjectionMatrix();
  }
  sizeRenderer();

  // ---- lighting ----
  scene.add(new THREE.AmbientLight(0xffffff, 0.65));
  const key = new THREE.DirectionalLight(0xffffff, 0.9);
  key.position.set(3, 4, 5);
  scene.add(key);
  const amberLight = new THREE.PointLight(0xf5a623, 1.1, 12);
  amberLight.position.set(-2, 1, 3);
  scene.add(amberLight);

  
  const docGroup = new THREE.Group();
  docGroup.rotation.set(-0.12, -0.42, 0.05);
  scene.add(docGroup);

  const paperGeo = new THREE.BoxGeometry(3.1, 4, 0.05, 1, 1, 1);
  const paperMat = new THREE.MeshStandardMaterial({
    color: 0xf7f6f2,
    roughness: 0.85,
    metalness: 0.02,
  });
  const paper = new THREE.Mesh(paperGeo, paperMat);
  docGroup.add(paper);

  const edgeGeo = new THREE.EdgesGeometry(paperGeo);
  const edgeMat = new THREE.LineBasicMaterial({ color: 0x1b1d27, opacity: 0.25, transparent: true });
  docGroup.add(new THREE.LineSegments(edgeGeo, edgeMat));

  // faint horizontal "text line" ridges
  const lineMat = new THREE.MeshBasicMaterial({ color: 0x2a2d3a, transparent: true, opacity: 0.16 });
  const lineWidths = [2.3, 2.5, 1.6, 2.5, 2.5, 1.9, 2.5, 2.2, 1.4];
  let y = 1.55;
  lineWidths.forEach((w, i) => {
    const h = i === 0 ? 0.16 : 0.07;
    const geo = new THREE.PlaneGeometry(w, h);
    const mesh = new THREE.Mesh(geo, lineMat);
    mesh.position.set(-1.55 + w / 2, y, 0.03);
    docGroup.add(mesh);
    y -= i === 0 ? 0.34 : 0.27;
  });

  // ---- scan line sweep ----
  const scanGeo = new THREE.PlaneGeometry(3.4, 0.5);
  const scanMat = new THREE.MeshBasicMaterial({
    color: 0xf5a623,
    transparent: true,
    opacity: 0.35,
    side: THREE.DoubleSide,
  });
  const scanLine = new THREE.Mesh(scanGeo, scanMat);
  scanLine.position.z = 0.06;
  docGroup.add(scanLine);

  // ---- drifting particles pulled off the document ----
  const PARTICLE_COUNT = 90;
  const positions = new Float32Array(PARTICLE_COUNT * 3);
  const speeds = new Float32Array(PARTICLE_COUNT);
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 4.5;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 5;
    positions[i * 3 + 2] = (Math.random() - 0.2) * 3;
    speeds[i] = 0.004 + Math.random() * 0.01;
  }
  const particleGeo = new THREE.BufferGeometry();
  particleGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const particleMat = new THREE.PointsMaterial({
    color: 0x3fc7b8,
    size: 0.045,
    transparent: true,
    opacity: 0.75,
    sizeAttenuation: true,
  });
  const particles = new THREE.Points(particleGeo, particleMat);
  scene.add(particles);

  // ---- mouse parallax ----
  let targetRotY = docGroup.rotation.y;
  let targetRotX = docGroup.rotation.x;
  window.addEventListener("mousemove", (e) => {
    const nx = (e.clientX / window.innerWidth) * 2 - 1;
    const ny = (e.clientY / window.innerHeight) * 2 - 1;
    targetRotY = -0.42 + nx * 0.18;
    targetRotX = -0.12 - ny * 0.1;
  });

  function renderStatic() {
    sizeRenderer();
    renderer.render(scene, camera);
  }

  if (reduceMotion) {
    renderStatic();
    window.addEventListener("resize", renderStatic);
    return;
  }

  const clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();

    scanLine.position.y = Math.sin(t * 0.7) * 1.9;
    scanMat.opacity = 0.22 + Math.abs(Math.sin(t * 0.7)) * 0.22;

    docGroup.rotation.y += (targetRotY - docGroup.rotation.y) * 0.04;
    docGroup.rotation.x += (targetRotX - docGroup.rotation.x) * 0.04;
    docGroup.position.y = Math.sin(t * 0.5) * 0.08;

    const pos = particleGeo.attributes.position.array;
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      pos[i * 3 + 1] += speeds[i];
      if (pos[i * 3 + 1] > 2.6) pos[i * 3 + 1] = -2.6;
    }
    particleGeo.attributes.position.needsUpdate = true;
    particles.rotation.y = t * 0.03;

    renderer.render(scene, camera);
  }

  window.addEventListener("resize", sizeRenderer);
  animate();
})();