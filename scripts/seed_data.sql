-- -- 1. INSERTAR ROLES (Administracion, Finanzas, Entrenadores, Clientes)
INSERT INTO rol (descripcion_rol, status_rol) VALUES 
('Administración', true), -- PostgreSQL le asignará el Id=1
('Finanzas', true),       -- PostgreSQL le asignará el Id=2
('Entrenadores', true),   -- PostgreSQL le asignará el Id=3
('Clientes', true);       -- PostgreSQL le asignará el Id=4

-- 2. INSERTAR USUARIOS (Uno por cada rol) 
-- Administrador (Rol 1)
INSERT INTO usuario (id_rol, correo, clave_hash, status_usuario) VALUES 
(1, 'administrador@smartgym.com', '$argon2i$v=19$m=16,t=2,p=1$c2VCV0RaZW1CUUlsOWN5aA$cI2EG6742JAzpshZKiREyw', true);

-- Usuario de Finanzas (Rol 2)
INSERT INTO usuario (id_rol, correo, clave_hash, status_usuario) VALUES 
(2, 'finanzas@smartgym.com', '$argon2i$v=19$m=16,t=2,p=1$VTNTT2lkNnV5N3VzOHZhSA$aJ28FG1SPle+2Ot9eItErg', true);

-- Usuario Entrenador (Rol 3)
INSERT INTO usuario (id_rol, correo, clave_hash, status_usuario) VALUES  
(3, 'entrenador1@smartgym.com', '$argon2i$v=19$m=16,t=2,p=1$ZFpVUHVKa3hhRXo2WjcxOA$jslGw7kAC6hvT08xEVHcxQ', true),
(3, 'entrenador2@smartgym.com', '$argon2i$v=19$m=16,t=2,p=1$QmdPV3E0UGlacFZwTklhZw$OWAeUNfEJsjMxV4uTbUByA', true),
(3, 'entrenador3@smartgym.com', '$argon2i$v=19$m=16,t=2,p=1$cEwxM2Y2REk2UnRSYkdkZg$btw3QZQ8YFo0bttZEKdo3A', true),
(3, 'entrenador4@smartgym.com', '$argon2i$v=19$m=16,t=2,p=1$akJ2N25samMwQVB2M2lJQQ$RVY1yMDVIGR70RMnQz5aYA', true),
(3, 'entrenador5@smartgym.com', '$argon2i$v=19$m=16,t=2,p=1$NktIdWVFelNvdDNFUGdSNQ$ed8NQzCXCNAYxOhLgxHr5A', true);

-- Usuario Cliente (Rol 4)
INSERT INTO usuario (id_rol, correo, clave_hash, status_usuario) VALUES
(4, 'ClienteR@gmail.com', '$argon2i$v=19$m=16,t=2,p=1$SWZXZWQ1YnlDREczZnZUUw$QlfbvRueXfvuzNRF9K7DxA', true),
(4, 'ClienteG@gmail.com', '$argon2i$v=19$m=16,t=2,p=1$U0szejE2NVBPRnU0OEpDOQ$Sa+10ZK3G2FweLyhfDI4uA', true),
(4, 'ClienteL@gmail.com', '$argon2i$v=19$m=16,t=2,p=1$YVo5aTBmb1YwRWVobENPYg$uhQua/8zBXjKyG6Qf3se+A', true),
(4, 'ClienteB@gmail.com', '$argon2i$v=19$m=16,t=2,p=1$MG9SclJDTW1XRjhidktGTA$gwvoXfkqGj+s0z6/CGU4IA', true),
(4, 'ClienteJ@gmail.com', '$argon2i$v=19$m=16,t=2,p=1$dGF2ZzBrajNXUVJlbXRYWg$dpewRiygdcRqiO3ZOio9qw', true),
(4, 'ClienteN@gmail.com', '$argon2i$v=19$m=16,t=2,p=1$MWY5ZGY3MXFDVHZvM3VwRA$zZ1TGE8e3sd6WajF1X8Eow', true);

-- 3. INSERTAR PLANES DE SUSCRIPCIÓN (Mensualidad basica, trimestre VIP, pase diario)
INSERT INTO plan (descripcion_plan, costo_plan, duracion_plan, status_plan) VALUES 
('Plan Mensualidad Básica', 25.00, 30, true), 
('Plan Trimestre VIP', 65.00, 90, true),
('Plan Pase Diario', 5.00, 1, true);

-- 4. INSERTAR PERFIL DEL ENTRENADOR 
INSERT INTO entrenador (cedula_entre, id_usuario, nombre_entre, apellido_entre, sueldo_entre, status_entre) VALUES 
('V-30042771', 3, 'Genesis', 'Carrasco', 300.00, true),
('V-31042771', 4, 'Nazareth', 'Vieira', 300.00, true),
('V-32042771', 5, 'Camila', 'Ramirez', 300.00, true),
('V-33042771', 6, 'Pablo', 'Sifontes', 300.00, true),
('V-34042771', 7, 'Ana', 'Montilla', 300.00, true);

-- 5. INSERTAR PERFIL DEL CLIENTE 
INSERT INTO cliente (cedula_cliente, id_usuario, nombre_cli, apellido_cli, status_cliente) VALUES
('V-31025997', 8, 'Ricardo', 'Gonzalez', true),
('V-32645824', 9, 'Geminis', 'Carrasco', true),
('V-12101157', 10, 'lolimar', 'Vieira', true),
('V-12101158', 11, 'Bellota', 'Carrasco', true),
('V-12101159', 12, 'Jose', 'Mendoza', true),
('V-12101150', 13, 'Nala', 'Vieira', true);

-- 6. INSERTAR CATEGORIA MAQUINA(Cardiovascular, Musculación, Peso Libre)
INSERT INTO categoria_maquina (descripcion_cate, status_categoria) VALUES 
('Cardiovascular', true), -- ID 1
('Musculación', true),    -- ID 2
('Peso Libre', true);     -- ID 3

-- 7. INSERTAR MAQUINA 
INSERT INTO maquina (id_categoria, nombre_maq, descripcion_maq, estado_oper_maq, status_maquina) VALUES 
(1, 'Caminadora', 'Motor 3.5 HP con inclinación', 'Activa', true),
(1, 'Bicicleta', 'Monitor de ritmo cardíaco', 'Activa', true),
(1, 'Escaladora', 'Resistencia ajustable', 'En mantenimiento', true),
(2, 'Prensa de Piernas 45°', 'Capacidad 500kg', 'Activa', true),
(2, 'Máquina Extensión', 'Aislamiento de cuádriceps', 'Fuera de servicio', true),
(3, 'Mancuernas', 'Juego de 2kg a 30kg', 'Activa', true); 

-- 8. INSERTAR PRODUCTOS
INSERT INTO producto (descripcion_produ, precio_actual, stock, status_producto) VALUES
('Proteina 1kg', 45.00, 15, true),
('Creatina 300g', 30.00, 20, true),
('Cinturón de Cuero L', 35.00, 6, true),
('Agua Mineral 500ml', 1.00, 99, true); 

-- 9. INSERTAR DISCIPLINAS
INSERT INTO disciplina (descripcion_disci, status_disciplina) VALUES 
('Spinning', true), 
('Yoga', true),
('Crossfit', true);

-- 10. INSERTAR BIOMETRIA CLIENTE
INSERT INTO biometria_cliente (cedula_cliente, cedula_entre, peso_cli, estatura_cli, porc_grasa_cli, observaciones, fecha_biometria, status_biometria ) VALUES
('V-31025997', 'V-30042771', 75.0, 1.78, 22.2, 'volumen.', '2026-06-02 08:00:00-04', true),
('V-32645824', 'V-31042771', 59.0, 1.65, 21.5, 'resistencia.', '2026-06-02 09:30:00-04', true),
('V-12101157', 'V-30042771', 60.0, 1.63, 22.4, 'definicion.', '2026-06-02 11:00:00-04', true);

-- 11. INSERTAR SESION DE CLASES
INSERT INTO sesion (cedula_entre, id_disciplina, fecha_inicio, fecha_final, cupos_disp, status_sesion) VALUES 
-- Sesión 1: Jueves 25 de Junio (Mañana)
('V-30042771', 2, '2026-06-25 08:00:00-04', '2026-06-25 09:30:00-04', 5, true),

-- Sesión 2: Jueves 25 de Junio (Mañana) (solapamiento)
('V-30042771', 3, '2026-06-25 08:00:00-04', '2026-06-25 09:30:00-04', 5, true),

-- Sesión 3: Miércoles 27 de Mayo (Noche)
('V-31042771', 3, '2026-05-27 07:00:00-04', '2026-05-27 20:30:00-04', 0, false);

-- 12. INSERTAR VENTA DE PRODUCTO
INSERT INTO venta_tienda (cedula_cliente, fecha_venta, monto_venta, status_venta) VALUES
('V-32645824', '2026-06-05 11:15:00-04', 1.00, true); 

-- 13. INSERTAR MEMBRESIA
INSERT INTO membresia (cedula_cliente, id_plan, fecha_inicio, fecha_venci, actividad_membre, status_membresia) VALUES 
('V-31025997', 1, '2026-06-01 07:00:00-04', '2026-07-01 07:00:00-04', 'Activa', true),     -- Ricardo 
('V-32645824', 2, '2026-05-20 07:00:00-04', '2026-06-20 07:00:00-04', 'Por Vencer', true), -- Geminis
('V-12101157', 2, '2026-05-05 08:00:00-04', '2026-06-05 23:59:59-04', 'Vencida', true);    -- Lolimar
