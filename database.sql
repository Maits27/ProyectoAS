
-- Crear la tabla de usuarios
CREATE TABLE usuarios (
    id CHAR(32) PRIMARY KEY,
    nombre VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    contrasena VARCHAR(255)
);

-- Crear la tabla de grupos
CREATE TABLE grupo (
    id CHAR(32) PRIMARY KEY,
    nombre VARCHAR(255) UNIQUE,
    contrasena VARCHAR(255)
);

-- Crear la tabla intermedia gruposUsuario
CREATE TABLE gruposUsuario (
    id CHAR(32) PRIMARY KEY,
    IdUsuario CHAR(32),
    IdGrupo CHAR(32),
    FOREIGN KEY (IdUsuario) REFERENCES usuarios(id),
    FOREIGN KEY (IdGrupo) REFERENCES grupo(id)
);