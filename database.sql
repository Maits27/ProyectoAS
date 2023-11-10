
-- Crear la tabla de usuarios
CREATE TABLE usuarios (
    id CHAR(64) PRIMARY KEY,
    nombre VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    contrasena VARCHAR(255)
);

-- Crear la tabla de grupos
CREATE TABLE proyecto (
    id CHAR(64) PRIMARY KEY,
    nombre VARCHAR(255) UNIQUE,
    contrasena VARCHAR(255)
);

-- Crear la tabla intermedia gruposUsuario
CREATE TABLE proyectosUsuario (
    id CHAR(64) PRIMARY KEY,
    IdUsuario CHAR(64),
    IdProyecto CHAR(64),
    FOREIGN KEY (IdUsuario) REFERENCES usuarios(id),
    FOREIGN KEY (IdProyecto) REFERENCES proyecto(id)
);


-- Insertar un usuario
INSERT INTO usuarios (id, nombre, email, contrasena)
VALUES ('1', 'root', 'root@root.com', 'root');

-- Insertar un proyecto
INSERT INTO proyecto (id, nombre, contrasena)
VALUES ('1', 'root', 'root');

-- Insertar la asociación entre el usuario y el proyecto en la tabla intermedia
INSERT INTO proyectosUsuario (id, IdUsuario, IdProyecto)
VALUES ('1', '1', '1');