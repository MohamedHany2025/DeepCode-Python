# Deployment Automation - CI/CD Pipeline Automation with Docker & Kubernetes
# Project: Deployment Automation
# Language: Python/YAML
# Description: CI/CD pipeline automation tool with containerization, health checks, and rollback capabilities

import yaml
import subprocess
import logging
import asyncio
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Enums ====================
class DeploymentStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class HealthStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

# ==================== Data Classes ====================
@dataclass
class HealthCheck:
    endpoint: str
    method: str = "GET"
    expected_status: int = 200
    timeout: int = 5
    interval: int = 10
    retries: int = 3

@dataclass
class Container:
    name: str
    image: str
    tag: str
    port: int
    environment_vars: Dict[str, str]

@dataclass
class KubernetesConfig:
    replicas: int = 3
    namespace: str = "default"
    cpu_request: str = "100m"
    memory_request: str = "128Mi"
    cpu_limit: str = "500m"
    memory_limit: str = "512Mi"

# ==================== Docker Manager ====================
class DockerManager:
    def __init__(self):
        self.registry = "docker.io"
    
    def build_image(self, dockerfile_path: str, tag: str, context: str = ".") -> bool:
        """Build Docker image"""
        try:
            cmd = f"docker build -t {tag} -f {dockerfile_path} {context}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully built image: {tag}")
                return True
            else:
                logger.error(f"Failed to build image: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error building image: {e}")
            return False
    
    def push_image(self, tag: str) -> bool:
        """Push image to registry"""
        try:
            cmd = f"docker push {tag}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully pushed image: {tag}")
                return True
            else:
                logger.error(f"Failed to push image: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error pushing image: {e}")
            return False
    
    def create_container(self, container: Container) -> bool:
        """Create and run Docker container"""
        try:
            env_args = " ".join([f"-e {k}={v}" for k, v in container.environment_vars.items()])
            cmd = f"docker run -d --name {container.name} -p {container.port}:8000 {env_args} {container.image}:{container.tag}"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Container created: {container.name}")
                return True
            else:
                logger.error(f"Failed to create container: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error creating container: {e}")
            return False
    
    def stop_container(self, container_name: str) -> bool:
        """Stop Docker container"""
        try:
            cmd = f"docker stop {container_name}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Container stopped: {container_name}")
                return True
            else:
                logger.error(f"Failed to stop container: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error stopping container: {e}")
            return False

# ==================== Kubernetes Manager ====================
class KubernetesManager:
    def __init__(self, kubeconfig: Optional[str] = None):
        self.kubeconfig = kubeconfig
    
    def _kubectl_cmd(self, args: str) -> str:
        """Build kubectl command"""
        cmd = "kubectl"
        if self.kubeconfig:
            cmd += f" --kubeconfig {self.kubeconfig}"
        return f"{cmd} {args}"
    
    def create_deployment(self, name: str, image: str, config: KubernetesConfig) -> bool:
        """Create Kubernetes deployment"""
        yaml_manifest = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
  namespace: {config.namespace}
spec:
  replicas: {config.replicas}
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
    spec:
      containers:
      - name: {name}
        image: {image}
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: {config.cpu_request}
            memory: {config.memory_request}
          limits:
            cpu: {config.cpu_limit}
            memory: {config.memory_limit}
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
"""
        try:
            with open(f"{name}-deployment.yaml", "w") as f:
                f.write(yaml_manifest)
            
            cmd = self._kubectl_cmd(f"apply -f {name}-deployment.yaml")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Deployment created: {name}")
                return True
            else:
                logger.error(f"Failed to create deployment: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error creating deployment: {e}")
            return False
    
    def scale_deployment(self, name: str, replicas: int, namespace: str = "default") -> bool:
        """Scale deployment replicas"""
        try:
            cmd = self._kubectl_cmd(f"scale deployment {name} --replicas={replicas} -n {namespace}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Deployment scaled: {name} -> {replicas} replicas")
                return True
            else:
                logger.error(f"Failed to scale deployment: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error scaling deployment: {e}")
            return False
    
    def rollout_status(self, name: str, namespace: str = "default") -> bool:
        """Check deployment rollout status"""
        try:
            cmd = self._kubectl_cmd(f"rollout status deployment/{name} -n {namespace}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Deployment healthy: {name}")
                return True
            else:
                logger.error(f"Deployment unhealthy: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error checking rollout: {e}")
            return False
    
    def rollback_deployment(self, name: str, namespace: str = "default") -> bool:
        """Rollback deployment to previous version"""
        try:
            cmd = self._kubectl_cmd(f"rollout undo deployment/{name} -n {namespace}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Deployment rolled back: {name}")
                return True
            else:
                logger.error(f"Failed to rollback deployment: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error rolling back deployment: {e}")
            return False

# ==================== Health Check Manager ====================
class HealthCheckManager:
    def __init__(self):
        self.checks: List[HealthCheck] = []
    
    async def check_health(self, url: str, timeout: int = 5) -> HealthStatus:
        """Check service health"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                return HealthStatus.HEALTHY if response.status_code == 200 else HealthStatus.UNHEALTHY
        except Exception as e:
            logger.error(f"Health check failed for {url}: {e}")
            return HealthStatus.UNHEALTHY
    
    async def monitor_health(self, url: str, check: HealthCheck) -> HealthStatus:
        """Monitor service with retries"""
        for attempt in range(check.retries):
            status = await self.check_health(url, check.timeout)
            if status == HealthStatus.HEALTHY:
                return HealthStatus.HEALTHY
            
            if attempt < check.retries - 1:
                await asyncio.sleep(1)
        
        return HealthStatus.UNHEALTHY

# ==================== Deployment Pipeline ====================
class DeploymentPipeline:
    def __init__(self):
        self.docker_manager = DockerManager()
        self.k8s_manager = KubernetesManager()
        self.health_manager = HealthCheckManager()
        self.status = DeploymentStatus.PENDING
        self.timestamp = datetime.now()
    
    async def deploy(
        self,
        app_name: str,
        dockerfile: str,
        image_tag: str,
        health_check: HealthCheck,
        k8s_config: KubernetesConfig
    ) -> DeploymentStatus:
        """Execute full deployment pipeline"""
        
        try:
            self.status = DeploymentStatus.IN_PROGRESS
            logger.info(f"Starting deployment: {app_name}")
            
            # Step 1: Build image
            logger.info("Step 1: Building Docker image...")
            if not self.docker_manager.build_image(dockerfile, image_tag):
                raise Exception("Failed to build image")
            
            # Step 2: Push image
            logger.info("Step 2: Pushing Docker image...")
            if not self.docker_manager.push_image(image_tag):
                raise Exception("Failed to push image")
            
            # Step 3: Deploy to Kubernetes
            logger.info("Step 3: Deploying to Kubernetes...")
            if not self.k8s_manager.create_deployment(app_name, image_tag, k8s_config):
                raise Exception("Failed to create Kubernetes deployment")
            
            # Step 4: Wait for rollout
            logger.info("Step 4: Waiting for rollout...")
            if not self.k8s_manager.rollout_status(app_name, k8s_config.namespace):
                raise Exception("Rollout failed")
            
            # Step 5: Health check
            logger.info("Step 5: Performing health checks...")
            health_url = f"http://{app_name}.{k8s_config.namespace}.svc.cluster.local{health_check.endpoint}"
            health_status = await self.health_manager.monitor_health(health_url, health_check)
            
            if health_status != HealthStatus.HEALTHY:
                logger.warning("Health check failed, rolling back...")
                self.k8s_manager.rollback_deployment(app_name, k8s_config.namespace)
                self.status = DeploymentStatus.ROLLED_BACK
                return self.status
            
            self.status = DeploymentStatus.SUCCESS
            logger.info(f"Deployment successful: {app_name}")
            return self.status
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            self.status = DeploymentStatus.FAILED
            return self.status

# ==================== Example Dockerfile ====================
DOCKERFILE_TEMPLATE = """
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \\
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

# ==================== Example usage ====================
if __name__ == "__main__":
    async def main():
        # Configuration
        app_name = "deepcode-app"
        image_tag = "deepcode/app:v1.0.0"
        
        health_check = HealthCheck(
            endpoint="/health",
            method="GET",
            expected_status=200
        )
        
        k8s_config = KubernetesConfig(
            replicas=3,
            namespace="production",
            cpu_request="100m",
            memory_request="256Mi"
        )
        
        # Execute deployment
        pipeline = DeploymentPipeline()
        status = await pipeline.deploy(
            app_name,
            "Dockerfile",
            image_tag,
            health_check,
            k8s_config
        )
        
        print(f"Deployment status: {status.value}")
    
    asyncio.run(main())
