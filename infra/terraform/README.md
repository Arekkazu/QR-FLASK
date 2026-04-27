# Manual de Despliegue IaC con Terraform (AWS EC2 Free Tier)

Este manual documenta la estructura y el proceso completo para desplegar:
- Infraestructura en AWS con Terraform.
- Proyecto QR-FLASK en una instancia EC2 de forma automatica.

## 1. Que despliega esta configuracion

Terraform crea los siguientes recursos:
- VPC dedicada.
- Subred publica.
- Internet Gateway.
- Tabla de rutas publica.
- Security Group (SSH + puerto de la app).
- Instancia EC2 Amazon Linux 2023 (`t2.micro` por defecto).

Durante el arranque de EC2 (`user_data`):
- Clona el repo desde GitHub en la rama definida.
- Crea entorno virtual de Python.
- Instala dependencias desde `requirements.txt`.
- Levanta la app con `gunicorn` como servicio `systemd`.

## 2. Estructura de archivos Terraform

- `providers.tf`: version de Terraform y proveedor AWS.
- `variables.tf`: variables de entrada.
- `main.tf`: red, seguridad y EC2.
- `user_data.sh.tftpl`: script de bootstrap y despliegue automatico.
- `outputs.tf`: salidas (IP publica, comando SSH, URL).
- `terraform.tfvars`: valores reales para este entorno.
- `terraform.tfvars.example`: plantilla de referencia.
- `.gitignore`: exclusion de estado/secretos de Terraform.

## 3. Prerrequisitos

Necesitas:
- Cuenta AWS activa.
- Key Pair creado en AWS EC2.
- Archivo `.pem` correspondiente en tu equipo local.
- AWS CLI instalado en el entorno donde correras Terraform.
- Terraform instalado en el entorno donde correras Terraform.

Si ejecutas desde WSL, instala y configura AWS CLI dentro de WSL.

## 4. Credenciales AWS (obligatorio)

El error `No valid credential sources found` se resuelve configurando credenciales en el mismo entorno donde ejecutas Terraform.

En WSL:

```bash
aws --version
aws configure
aws sts get-caller-identity
```

Debes ver una respuesta valida en `get-caller-identity` antes de correr `terraform plan`.

## 5. Variables del despliegue

El archivo `terraform.tfvars` ya contiene una base funcional. Revisa especialmente:

- `aws_region`: region objetivo (`us-east-1` recomendada por costo para pruebas).
- `instance_type`: `t2.micro`.
- `ssh_key_name`: nombre exacto del Key Pair en AWS.
- `ssh_cidr`: IP publica permitida para SSH, ejemplo `185.229.216.235/32`.
- `repo_url`: URL del repositorio a desplegar.
- `repo_branch`: rama de despliegue (actualmente `deploy`).
- `app_port`: puerto expuesto (5000).

## 6. Flujo de despliegue paso a paso

Desde la carpeta `infra/terraform`:

```bash
terraform init
terraform validate
terraform plan -out tfplan
terraform apply tfplan
```

Al finalizar, consulta salidas:

```bash
terraform output
```

Salidas clave:
- `public_ip`
- `ssh_command`
- `app_url`

## 7. Verificacion en la instancia

Conectate por SSH usando tu `.pem`:

```bash
ssh -i ../../test-qrflask.pem ec2-user@<PUBLIC_IP>
```

Verifica el servicio:

```bash
sudo systemctl status qr-flask
sudo journalctl -u qr-flask -f
```

Si el servicio no existe, revisa estos logs en la instancia para ver si `user_data` fallo durante el primer arranque:

```bash
sudo tail -n 200 /var/log/cloud-init-output.log
sudo cat /var/lib/cloud/instance/user-data.txt
```

Importante: `user_data` solo se ejecuta cuando la instancia se crea por primera vez. Si cambiaste Terraform despues de crear la EC2, un nuevo `terraform apply` no vuelve a ejecutar ese bootstrap. En ese caso, recrea la instancia o fuerza su reemplazo:

```bash
terraform apply -replace=aws_instance.app
```

Eso volvera a correr todo el bootstrap y deberia crear `qr-flask.service`.

Prueba en navegador:
- `http://<PUBLIC_IP>:5000`

## 8. Como se realiza el despliegue de la app

En `user_data.sh.tftpl` se hace lo siguiente:
- Instalacion de paquetes base (`git`, `python3`, `pip`).
- Clonado/actualizacion del repositorio en `/opt/<project_name>`.
- Creacion de `.venv` e instalacion de dependencias.
- Creacion del servicio `systemd`:
  - Ejecuta `gunicorn --bind 0.0.0.0:<app_port> wsgi:app`.
  - Reinicio automatico en caso de falla.

## 9. Como actualizar a una nueva version del proyecto

### Opcion A: recrear aplicando cambios de Terraform
- Actualiza la rama `deploy` en GitHub.
- Ejecuta `terraform apply`.

Nota: si no cambian recursos, EC2 no se recrea y `user_data` no corre de nuevo.

### Opcion B: actualizar sin recrear infraestructura
En la EC2:

```bash
cd /opt/qr-flask
sudo -u ec2-user git fetch origin
sudo -u ec2-user git checkout deploy
sudo -u ec2-user git pull origin deploy
sudo -u ec2-user ./.venv/bin/pip install -r requirements.txt
sudo systemctl restart qr-flask
```

## 10. Destruccion de infraestructura

Para evitar costos:

```bash
terraform destroy
```

## 11. Problemas comunes

### Error: No valid credential sources found
- No hay credenciales AWS en el entorno actual.
- Ejecuta `aws configure` y valida con `aws sts get-caller-identity`.

### Error: InvalidKeyPair.NotFound
- `ssh_key_name` no coincide con el nombre del Key Pair en AWS.

### App no responde en puerto 5000
- Revisa `app_cidr` y Security Group.
- Revisa logs: `sudo journalctl -u qr-flask -f`.

### Repo privado no clona
- Debes configurar autenticacion para `git clone` en EC2 (deploy key o token).

## 12. Buenas practicas

- Mantener `ssh_cidr` en `/32` con tu IP publica.
- No abrir SSH a `0.0.0.0/0`.
- No subir `.pem`, `terraform.tfvars` ni `.tfstate` al repositorio.
- Ejecutar `terraform destroy` al terminar pruebas.
