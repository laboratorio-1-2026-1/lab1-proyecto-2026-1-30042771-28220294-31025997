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
(3, 'entrenador1@smartgym.com', '$argon2i$v=19$m=16,t=2,p=1$ZFpVUHVKa3hhRXo2WjcxOA$jslGw7kAC6hvT08xEVHcxQ', true);

-- Usuario Cliente (Rol 4)
INSERT INTO usuario (id_rol, correo, clave_hash, status_usuario) VALUES
(4, 'cliente@gmail.com', '$argon2i$v=19$m=16,t=2,p=1$MjlEb0ladnRZZ3ljaDdyaA$6nEj6VQq8dTzcwoh2pGzqw', true),
(4, 'ClienteGenesis@gmail.com', '$argon2i$v=19$m=16,t=2,p=1$SlpFa3BqNWc4aFU4VVpUQg$rE5H27Oee0Vpd7XQch9+aA', true),
(4, 'ClienteMaria@gmail.com', '$argon2i$v=19$m=16,t=2,p=1$S1RMRkxaaU91R3lmZ1FFSQ$iNO61MzMzK4QPxa9m1v3dA', true); 


-- 3. INSERTAR PLANES DE SUSCRIPCIÓN (Mensualidad basica, trimestre VIP, pase diario)
INSERT INTO plan (descripcion_plan, costo_plan, duracion_plan, status_plan) VALUES 
('Plan Mensualidad Básica', 25.00, 30, true), 
('Plan Trimestre VIP', 65.00, 90, true),
('Plan Pase Diario', 5.00, 1, true);

-- 4. INSERTAR PRODUCTOS PARA LA TIENDA 
INSERT INTO producto (descripcion_produ, precio_actual, stock, status_producto) VALUES 
('Proteína 1kg', 45.00, 15, true),
('Creatina 300g', 30.00, 20, true),
('Barra energetica', 2.00, 50, true),
('Cinturón de Cuero L', 35.00, 5, true),
('Agua Mineral 500ml', 1.00, 100, true);

-- 5. INSERTAR PERFIL DEL ENTRENADOR 
INSERT INTO entrenador (cedula_entre, id_usuario, nombre_entre, apellido_entre, sueldo_entre, status_entre) VALUES 
('V-30042771', 3, 'Genesis', 'Carrasco', 300.00, true);

-- 6. INSERTAR PERFIL DEL CLIENTE (Vinculados a los usuarios 4, 5 y 6)
INSERT INTO cliente (cedula_cliente, id_usuario, nombre_cli, apellido_cli, status_cliente) VALUES
('V-31025997', 4, 'Ricardo', 'Gonzales', true),
('V-32645824', 5, 'Geminis', 'Carrasco', true),
('V-12101157', 6, 'lolimar', 'vieira', true);

-- 7. INSERTAR CATEGORIA MAQUINA(Cardiovascular, Musculación, Peso Libre)
INSERT INTO categoria_maquina (descripcion_cate, status_categoria) VALUES 
('Cardiovascular', true), -- ID 1
('Musculación', true),    -- ID 2
('Peso Libre', true);     -- ID 3

-- 8. INSERTAR MAQUINA 
INSERT INTO maquina (id_categoria, nombre_maq, descripcion_maq, estado_oper_maq, status_maquina) VALUES 
(1, 'Caminadora', 'Motor 3.5 HP con inclinación', 'Activa', true),
(1, 'Bicicleta', 'Monitor de ritmo cardíaco', 'Activa', true),
(1, 'Escaladora', 'Resistencia ajustable', 'En mantenimiento', true),
(2, 'Prensa de Piernas 45°', 'Capacidad 500kg', 'Activa', true),
(2, 'Máquina Extensión', 'Aislamiento de cuádriceps', 'Fuera de servicio', true),
(3, 'Mancuernas', 'Juego de 2kg a 30kg', 'Activa', true); 

-- 9. INSERTAR PRODUCTOS
INSERT INTO producto (descripcion_produ, precio_actual, stock, status_producto) VALUES
('Proteina 1kg', 45, 15, true),
('Creatina 300g', 30, 20, true),
('Cinturón de Cuero L', 35, 4, true),
('Agua Mineral 500ml', 1, 99, true); 