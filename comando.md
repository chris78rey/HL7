# Subir Repositorio a GitHub por SSH

## 1. Ir al proyecto

```bash
cd /home/integracioneshe1/vscode_proj/HL7FINAL
```

## 2. Crear clave SSH

```bash
ssh-keygen -t ed25519 -C "chris78rey"
```

## 3. Mostrar la clave publica

```bash
cat ~/.ssh/id_ed25519.pub
```

## 4. Agregar la clave en GitHub

Ve a:

`Settings` -> `SSH and GPG keys` -> `New SSH key`

Pega ahi la salida completa del comando anterior.

## 5. Probar autenticacion SSH con GitHub

```bash
ssh -T git@github.com
```

## 6. Cambiar el remoto del repositorio a SSH

```bash
cd /home/integracioneshe1/vscode_proj/HL7FINAL
git remote set-url origin git@github.com:chris78rey/hl7_he1_respaldo2026.git
```

## 7. Verificar el remoto

```bash
git remote -v
```

## 8. Subir la rama main

```bash
git push -u origin main
```

## 9. Si pregunta por primera conexion

```bash
yes
```

## 10. Verificar despues del push

```bash
git branch -vv
```

```bash
git status
```
