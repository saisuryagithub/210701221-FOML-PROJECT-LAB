import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('3d-model-container');

  // Create a scene, camera, and renderer
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer();

  renderer.setSize(window.innerWidth, window.innerHeight);
  container.appendChild(renderer.domElement);

  // Position the camera
  camera.position.z = 5;

  // Load the 3D model
  const loader = new GLTFLoader();
  loader.load('https://example.com/Nike Shoe V2.glb', (gltf) => {
    const model = gltf.scene;
    scene.add(model);
  });

  // Create a render loop
  const animate = function () {
    requestAnimationFrame(animate);

    // Render the scene
    renderer.render(scene, camera);
  };

  animate();
});