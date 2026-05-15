-- -- 1. INSERTAR ROLES (Administracion, Finanzas, Entrenadores, Clientes)
INSERT INTO rol (descripcion_rol, status_rol) VALUES 
('Administración', true), -- PostgreSQL le asignará el Id=1
('Finanzas', true),       -- PostgreSQL le asignará el Id=2
('Entrenadores', true),   -- PostgreSQL le asignará el Id=3
('Clientes', true);       -- PostgreSQL le asignará el Id=4


-- 2. INSERTAR USUARIOS INICIALES (Uno por cada rol)
-- Administrador (Rol 1)
INSERT INTO usuario (id_rol, correo, clave_hash, status_usuario) 
VALUES (1, 'administrador@smartgym.com', 'admin123', true);

-- Usuario de Finanzas (Rol 2)
INSERT INTO usuario (id_rol, correo, clave_hash, status_usuario) 
VALUES (2, 'finanzas@smartgym.com', 'finanzas123', true);

-- Usuario Entrenador (Rol 3)
INSERT INTO usuario (id_rol, correo, clave_hash, status_usuario) 
VALUES (3, 'entrenador1@smartgym.com', 'entrenador123', true);

-- Usuario Cliente (Rol 4)
INSERT INTO usuario (id_rol, correo, clave_hash, status_usuario) 
VALUES (4, 'cliente@gmail.com', 'cliente123', true);


-- 3. INSERTAR PLANES DE ENTRENAMIENTO (Mensualidad basica, trimestre VIP, pase diario)
INSERT INTO plan (descripcion_plan, costo_plan, duracion_plan, status_plan) VALUES 
('Plan Mensualidad Básica', 25.00, 30, true), 
('Plan Trimestre VIP', 65.00, 90, true),
('Plan Pase Diario', 5.00, 1, true);

-- 4. Insertar productos para la tienda
INSERT INTO producto (descripcion_produ, precio_actual, stock, status_producto) VALUES 
('Proteína 1kg', 45.00, 15, true),
('Creatina 300g', 30.00, 20, true),
('Barra energetica', 2.00, 50, true),
('Cinturón de Cuero L', 35.00, 5, true),
('Agua Mineral 500ml', 1.00, 100, true);

-- 5. Insertar Perfil del entrenador
INSERT INTO entrenador (cedula_entre, id_usuario, nombre_entre, apellido_entre, sueldo_entre, status_entre) 
VALUES ('V-30042771', 3, 'Genesis', 'Carrasco', 300.00, true);

-- 6. Insertar Perfil del cliente
INSERT INTO cliente (cedula_cliente, id_usuario, nombre_cli, apellido_cli, status_cliente) 
VALUES ('V-31025997', 4, 'Ricardo', 'Gonzales', true);