# 📱 Manual de Usuario - Sistema de Asistencias QR

## 🌟 Bienvenido al Sistema

Este sistema permite registrar asistencias de forma rápida y segura utilizando códigos QR dinámicos. Cada usuario tiene un código único que se actualiza automáticamente para mayor seguridad.

---

## 🚀 Primeros Pasos

### 1. Acceso al Sistema
- Abre tu navegador web
- Ve a la dirección: `http://localhost:5000` (o la que te proporcione tu administrador)
- Verás la pantalla de inicio de sesión

### 2. Iniciar Sesión
- Ingresa tu **nombre de usuario** y **contraseña**
- Haz clic en **"Ingresar"**
- Serás redirigido automáticamente según tu rol

---

## 👤 Para Usuarios Regulares

### Tu Dashboard Personal

Después de iniciar sesión verás:

#### 🔲 Tu Código QR Personal
- **Se actualiza automáticamente cada 60 segundos**
- Es único y está vinculado a tu cuenta
- Solo es válido por tiempo limitado para mayor seguridad

#### 📊 Tu Historial de Asistencias
- Lista de todos tus registros anteriores
- Fechas y horas de cada asistencia
- Estado de cada registro

### Cómo Registrar tu Asistencia

1. **Muestra tu código QR** al administrador o persona encargada
2. Ellos lo escanearán con el sistema
3. **¡Listo!** Tu asistencia quedará registrada automáticamente

#### ⚠️ Importante:
- Solo puedes registrar **una asistencia por día**
- El código QR expira después de 60 segundos
- Si expira, simplemente recarga la página para obtener uno nuevo

### Actualizar tu Perfil

1. Ve a **"Mi Perfil"** desde el menú
2. Puedes cambiar:
   - Tu nombre de usuario
   - Tu contraseña (opcional)
3. Haz clic en **"Actualizar Perfil"**

---

## 👑 Para Administradores

### Panel de Administración

Como administrador tienes acceso a:

#### 👥 Gestión de Usuarios
- **Ver todos los usuarios** del sistema
- **Crear nuevos usuarios** con roles específicos
- **Editar información** de usuarios existentes
- **Eliminar usuarios** (con restricciones de seguridad)

#### 📷 Registrar Asistencias

### Usar el Escáner QR

#### Método 1: Cámara Web (Recomendado)
1. Ve a **"Registrar Asistencia"**
2. Haz clic en **"Iniciar Cámara"**
3. **Permite el acceso** a la cámara cuando el navegador lo solicite
4. **Enfoca el código QR** del usuario
5. El sistema registrará automáticamente la asistencia

#### Método 2: Ingreso Manual
Si la cámara no funciona:
1. Haz clic en **"Ingreso Manual"**
2. **Copia y pega** el código QR del usuario
3. Haz clic en **"Registrar"**

#### Método 3: Desde Archivo
1. Haz clic en **"Desde Archivo"**
2. **Selecciona una imagen** que contenga el código QR
3. El sistema lo procesará automáticamente

### Gestionar Usuarios

#### Crear Nuevo Usuario
1. En el panel de administración, haz clic en **"Agregar Usuario"**
2. Completa los datos:
   - **Nombre de usuario** (debe ser único)
   - **Contraseña** (segura)
   - **Rol** (Usuario o Administrador)
3. Haz clic en **"Crear Usuario"**

#### Editar Usuario Existente
1. Encuentra al usuario en la lista
2. Haz clic en el botón **amarillo** (editar)
3. Modifica los campos necesarios
4. Haz clic en **"Actualizar Usuario"**

#### Eliminar Usuario
1. Haz clic en el botón **rojo** (eliminar)
2. **Confirma la acción** (¡No se puede deshacer!)
3. El usuario será eliminado permanentemente

⚠️ **Restricciones de seguridad:**
- No puedes eliminar tu propia cuenta mientras estés conectado
- No puedes eliminar el último administrador del sistema

---

## 🔒 Seguridad del Sistema

### Códigos QR Seguros
- **Firmados digitalmente** con criptografía HMAC
- **Expiración automática** cada 60 segundos
- **Únicos por usuario** y sesión
- **No reutilizables** después de expirar

### Protección de Datos
- **Contraseñas encriptadas** en la base de datos
- **Sesiones seguras** con tokens únicos
- **Control de acceso** basado en roles
- **Registro único diario** (no se puede duplicar)

---

## 🔧 Solución de Problemas

### Problemas con la Cámara

#### "Error al iniciar la cámara" o "Camera streaming not supported"

**Causas comunes:**
- El navegador no tiene permisos para acceder a la cámara
- Estás usando HTTP en lugar de HTTPS
- El navegador no es compatible
- No hay cámara disponible en el dispositivo

**Soluciones:**

1. **Permitir acceso a la cámara:**
   - Busca el ícono de cámara en la barra de direcciones
   - Haz clic y selecciona "Permitir"
   - Recarga la página

2. **Usar HTTPS:**
   - Los navegadores modernos requieren HTTPS para acceder a la cámara
   - Contacta al administrador para configurar HTTPS

3. **Probar otro navegador:**
   - **Recomendados:** Chrome, Firefox, Edge
   - **Evitar:** Internet Explorer, navegadores muy antiguos

4. **Usar alternativas:**
   - **Ingreso Manual:** Copia y pega el código
   - **Desde Archivo:** Sube una imagen del código QR

### Problemas de Códigos QR

#### "Token QR inválido o expirado"
- **Causa:** El código QR ha expirado (más de 60 segundos)
- **Solución:** Pedir al usuario que recargue su página para obtener un código nuevo

#### "Ya se registró asistencia para este usuario hoy"
- **Causa:** El usuario ya registró su asistencia en el día actual
- **Información:** Esta es una característica de seguridad, solo se permite una asistencia por día

### Problemas de Acceso

#### "Usuario o contraseña incorrectos"
- Verificar que los datos estén escritos correctamente
- Contactar al administrador para restablecer la contraseña

#### "Acceso denegado"
- Tu cuenta no tiene permisos para acceder a esa sección
- Solo los administradores pueden acceder al panel de administración

---

## 📞 Contacto y Soporte

### Para Usuarios
- Contacta a tu administrador de sistema
- Verifica que estés usando un navegador compatible
- Asegúrate de tener una conexión estable a internet

### Para Administradores
- Consulta los logs del servidor para errores técnicos
- Verifica la configuración de la base de datos
- Revisa los permisos de archivos del sistema

---

## 💡 Consejos y Mejores Prácticas

### Para un Mejor Rendimiento

1. **Usa navegadores modernos:**
   - Chrome 90+
   - Firefox 85+
   - Safari 14+
   - Edge 90+

2. **Asegurate de tener buena iluminación** al escanear códigos QR

3. **Mantén el código QR estable** durante el escaneo

4. **Usa HTTPS** en producción para mejor seguridad

### Para Administradores

1. **Crea contraseñas seguras** para todos los usuarios
2. **Revisa regularmente** los registros de asistencia
3. **Mantén backup** de la base de datos
4. **Actualiza el sistema** regularmente

---

## 📋 Resumen de Funcionalidades

### ✅ Lo que SÍ puedes hacer:
- Ver tu código QR personal actualizado
- Registrar una asistencia por día
- Actualizar tu perfil personal
- Ver tu historial de asistencias
- (Admin) Gestionar usuarios
- (Admin) Registrar asistencias de otros usuarios

### ❌ Lo que NO puedes hacer:
- Registrar múltiples asistencias el mismo día
- Usar códigos QR expirados
- Acceder a funciones de administrador sin permisos
- Eliminar tu propia cuenta mientras estés conectado
- (Admin) Eliminar el último administrador

---

**¡Gracias por usar el Sistema de Asistencias QR!** 🎉

Para más ayuda, contacta a tu administrador de sistema.