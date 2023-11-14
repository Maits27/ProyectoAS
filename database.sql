
-- Crear la tabla de usuarios
CREATE TABLE usuarios (
    id CHAR(64) PRIMARY KEY,
    nombre VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE,
    contrasena VARCHAR(255)
);

-- Crear la tabla de grupos
CREATE TABLE proyecto (
    id CHAR(64) PRIMARY KEY,
    nombre VARCHAR(255) UNIQUE,
    contrasena VARCHAR(255), 
    presupuesto INT, 
    presupuestoInicial INT,
    main VARCHAR(255)
);

-- Crear la tabla intermedia gruposUsuario
CREATE TABLE proyectosUsuario (
    id CHAR(64) PRIMARY KEY,
    IdUsuario CHAR(64),
    IdProyecto CHAR(64),
    FOREIGN KEY (IdUsuario) REFERENCES usuarios(id),
    FOREIGN KEY (IdProyecto) REFERENCES proyecto(id)
);


CREATE TABLE transaccion (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    nombre VARCHAR(255),
    gasto INT,
    valor FLOAT,
    IdUsuario CHAR(64),
    IdProyecto CHAR(64),
    FOREIGN KEY (IdUsuario) REFERENCES usuarios(id),
    FOREIGN KEY (IdProyecto) REFERENCES proyecto(id)
);

CREATE TABLE producto(
    id INT AUTO_INCREMENT PRIMARY KEY, -- igual se puede hacer hash
    nombre VARCHAR(255),
    categoria VARCHAR(255),
    cantidad INT,
    precioUnidad FLOAT,
    IdTransaccion INT,
    FOREIGN KEY (IdTransaccion) REFERENCES transaccion(id)
);