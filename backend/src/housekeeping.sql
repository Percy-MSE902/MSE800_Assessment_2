-- =====================================================
-- Housekeeping Hotel Management System Database
-- Roles: admin, guest, cleaner
-- =====================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- 1. User Table
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL COMMENT 'Username',
  `password` varchar(255) NOT NULL COMMENT 'Password (encrypted)',
  `full_name` varchar(100) NOT NULL COMMENT 'Full name',
  `email` varchar(100) DEFAULT NULL COMMENT 'Email',
  `phone` varchar(20) DEFAULT NULL COMMENT 'Phone number',
  `role` varchar(20) NOT NULL DEFAULT 'guest' COMMENT 'Role: admin/guest/cleaner',
  `status` int NOT NULL DEFAULT 1 COMMENT 'Status: 0 disabled, 1 active',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modify_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` int NOT NULL DEFAULT 0 COMMENT 'Soft delete: 0 normal, 1 deleted',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  KEY `idx_role` (`role`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User table';

-- ----------------------------
-- 2. Room Table
-- ----------------------------
DROP TABLE IF EXISTS `room`;
CREATE TABLE `room` (
  `room_id` int NOT NULL AUTO_INCREMENT,
  `room_number` varchar(20) NOT NULL COMMENT 'Room number',
  `floor` int NOT NULL COMMENT 'Floor',
  `room_type` varchar(30) NOT NULL COMMENT 'Room type: Single/Double/Suite/Deluxe Suite',
  `capacity` int NOT NULL DEFAULT 2 COMMENT 'Capacity',
  `price` decimal(10,2) NOT NULL COMMENT 'Price',
  `status` int NOT NULL DEFAULT 0 COMMENT 'Status: 0 vacant, 1 occupied, 2 cleaning, 3 pending inspection, 4 maintenance',
  `last_clean_time` datetime DEFAULT NULL COMMENT 'Last cleaning time',
  `description` varchar(500) DEFAULT NULL COMMENT 'Room description',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modify_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`room_id`),
  UNIQUE KEY `uk_room_number` (`room_number`),
  KEY `idx_status` (`status`),
  KEY `idx_floor` (`floor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Room table';

-- ----------------------------
-- 3. Service Type Table
-- ----------------------------
DROP TABLE IF EXISTS `service_type`;
CREATE TABLE `service_type` (
  `type_id` int NOT NULL AUTO_INCREMENT,
  `type_name` varchar(50) NOT NULL COMMENT 'Service type name',
  `description` varchar(200) DEFAULT NULL COMMENT 'Description',
  `standard_time` int NOT NULL DEFAULT 30 COMMENT 'Standard time (minutes)',
  `price` decimal(10,2) NOT NULL DEFAULT 0.00 COMMENT 'Price',
  `is_active` int NOT NULL DEFAULT 1 COMMENT 'Is active',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modify_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Service type table';

-- ----------------------------
-- 4. Service Order Table (Core)
-- ----------------------------
DROP TABLE IF EXISTS `service_order`;
CREATE TABLE `service_order` (
  `order_id` int NOT NULL AUTO_INCREMENT,
  `order_no` varchar(30) NOT NULL COMMENT 'Order number',
  `room_id` int NOT NULL COMMENT 'Room ID',
  `guest_id` int NOT NULL COMMENT 'Guest ID',
  `service_type_id` int NOT NULL COMMENT 'Service type ID',
  `assigned_staff_id` int DEFAULT NULL COMMENT 'Assigned staff ID',
  
  `status` int NOT NULL DEFAULT 0 COMMENT 'Status: 0 pending, 1 assigned, 2 cleaning, 3 pending inspection, 4 completed, 5 cancelled',
  `priority` int NOT NULL DEFAULT 0 COMMENT 'Priority: 0 normal, 1 urgent, 2 emergency',
  
  `request_time` datetime NOT NULL COMMENT 'Request time',
  `scheduled_start` datetime DEFAULT NULL COMMENT 'Scheduled start time',
  `scheduled_end` datetime DEFAULT NULL COMMENT 'Scheduled end time',
  `actual_start` datetime DEFAULT NULL COMMENT 'Actual start time',
  `actual_complete` datetime DEFAULT NULL COMMENT 'Actual completion time',
  
  `remarks` varchar(500) DEFAULT NULL COMMENT 'Remarks',
  `guest_feedback` varchar(500) DEFAULT NULL COMMENT 'Guest feedback',
  `rating` int DEFAULT NULL COMMENT 'Rating 1-5',
  
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modify_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`order_id`),
  UNIQUE KEY `uk_order_no` (`order_no`),
  KEY `idx_room_id` (`room_id`),
  KEY `idx_guest_id` (`guest_id`),
  KEY `idx_staff_id` (`assigned_staff_id`),
  KEY `idx_status` (`status`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Service order table';

-- ----------------------------
-- 5. Cleaning Inspection Table
-- ----------------------------
DROP TABLE IF EXISTS `inspection`;
CREATE TABLE `inspection` (
  `inspection_id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL COMMENT 'Order ID',
  `inspector_id` int NOT NULL COMMENT 'Inspector ID (supervisor)',
  `cleaner_id` int NOT NULL COMMENT 'Cleaner ID',
  
  `status` int NOT NULL DEFAULT 0 COMMENT 'Status: 0 pending inspection, 1 passed, 2 failed',
  `score` int DEFAULT NULL COMMENT 'Score 0-100',
  `issues` text COMMENT 'Issues description',
  `photos` text COMMENT 'Inspection photos (JSON array)',
  `inspection_time` datetime NOT NULL COMMENT 'Inspection time',
  `reinspection_time` datetime DEFAULT NULL COMMENT 'Reinspection time',
  
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modify_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`inspection_id`),
  KEY `idx_order_id` (`order_id`),
  KEY `idx_inspector_id` (`inspector_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Cleaning inspection table';

-- ----------------------------
-- 6. Inventory Item Table
-- ----------------------------
DROP TABLE IF EXISTS `inventory_item`;
CREATE TABLE `inventory_item` (
  `item_id` int NOT NULL AUTO_INCREMENT,
  `item_name` varchar(50) NOT NULL COMMENT 'Item name',
  `category` varchar(30) NOT NULL COMMENT 'Category: Textile/Toiletries/Cleaning Supplies/Consumables',
  `quantity` int NOT NULL DEFAULT 0 COMMENT 'Current quantity',
  `min_stock` int NOT NULL DEFAULT 10 COMMENT 'Minimum stock threshold',
  `unit` varchar(10) NOT NULL COMMENT 'Unit',
  `location` varchar(50) DEFAULT NULL COMMENT 'Storage location',
  `is_active` int NOT NULL DEFAULT 1 COMMENT 'Is active',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modify_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`item_id`),
  KEY `idx_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Inventory item table';

-- ----------------------------
-- 7. Item Consumption Record Table
-- ----------------------------
DROP TABLE IF EXISTS `consumption`;
CREATE TABLE `consumption` (
  `consumption_id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL COMMENT 'Order ID',
  `item_id` int NOT NULL COMMENT 'Item ID',
  `quantity` int NOT NULL COMMENT 'Quantity consumed',
  `remarks` varchar(200) DEFAULT NULL COMMENT 'Remarks',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`consumption_id`),
  KEY `idx_order_id` (`order_id`),
  KEY `idx_item_id` (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Item consumption record table';

-- ----------------------------
-- 8. Staff Schedule Table
-- ----------------------------
DROP TABLE IF EXISTS `schedule`;
CREATE TABLE `schedule` (
  `schedule_id` int NOT NULL AUTO_INCREMENT,
  `staff_id` int NOT NULL COMMENT 'Staff ID',
  `work_date` date NOT NULL COMMENT 'Work date',
  `shift` int NOT NULL COMMENT 'Shift: 0 day, 1 evening, 2 night',
  `start_time` time NOT NULL COMMENT 'Start time',
  `end_time` time NOT NULL COMMENT 'End time',
  `status` int NOT NULL DEFAULT 1 COMMENT 'Status: 0 off, 1 working, 2 on leave',
  `remarks` varchar(200) DEFAULT NULL COMMENT 'Remarks',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modify_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`schedule_id`),
  UNIQUE KEY `uk_staff_date` (`staff_id`, `work_date`),
  KEY `idx_work_date` (`work_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Staff schedule table';

-- ----------------------------
-- 9. Guest Review Table
-- ----------------------------
DROP TABLE IF EXISTS `review`;
CREATE TABLE `review` (
  `review_id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL COMMENT 'Order ID',
  `guest_id` int NOT NULL COMMENT 'Guest ID',
  `rating` int NOT NULL COMMENT 'Rating 1-5',
  `comment` varchar(500) DEFAULT NULL COMMENT 'Review content',
  `images` text COMMENT 'Review images (JSON array)',
  `reply` varchar(500) DEFAULT NULL COMMENT 'Business reply',
  `reply_time` datetime DEFAULT NULL COMMENT 'Reply time',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_deleted` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`review_id`),
  KEY `idx_order_id` (`order_id`),
  KEY `idx_guest_id` (`guest_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Guest review table';

-- ----------------------------
-- 10. Announcement Table
-- ----------------------------
DROP TABLE IF EXISTS `announcement`;
CREATE TABLE `announcement` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL COMMENT 'Title',
  `content` text NOT NULL COMMENT 'Content',
  `target_role` varchar(20) DEFAULT NULL COMMENT 'Target role: admin/cleaner/guest/all',
  `is_published` int NOT NULL DEFAULT 0 COMMENT 'Is published',
  `publish_time` datetime DEFAULT NULL COMMENT 'Publish time',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modify_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Announcement table';

-- ----------------------------
-- Initial Data
-- ----------------------------

-- Insert admin account (password: admin123)
INSERT INTO `user` (`username`, `password`, `full_name`, `email`, `phone`, `role`, `status`) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.z7aO.S', 'System Admin', 'admin@hotel.com', '13800000000', 'admin', 1);

-- Insert guest accounts
INSERT INTO `user` (`username`, `password`, `full_name`, `email`, `phone`, `role`, `status`) VALUES
('guest1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.z7aO.S', 'Zhang San', 'zhangsan@email.com', '13800000001', 'guest', 1),
('guest2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.z7aO.S', 'Li Si', 'lisi@email.com', '13800000002', 'guest', 1);

-- Insert cleaner accounts
INSERT INTO `user` (`username`, `password`, `full_name`, `email`, `phone`, `role`, `status`) VALUES
('cleaner1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.z7aO.S', 'Cleaner Zhang San', 'cleaner1@hotel.com', '13900000001', 'cleaner', 1),
('cleaner2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.z7aO.S', 'Cleaner Li Si', 'cleaner2@hotel.com', '13900000002', 'cleaner', 1);

-- Insert room data
INSERT INTO `room` (`room_number`, `floor`, `room_type`, `capacity`, `price`, `status`) VALUES
('1001', 1, 'Single Room', 1, 199.00, 0),
('1002', 1, 'Double Room', 2, 299.00, 1),
('1003', 1, 'Single Room', 1, 199.00, 2),
('1004', 1, 'Suite', 3, 599.00, 3),
('2001', 2, 'Double Room', 2, 299.00, 0),
('2002', 2, 'Double Room', 2, 299.00, 1),
('2003', 2, 'Suite', 3, 599.00, 0),
('3001', 3, 'Deluxe Suite', 4, 999.00, 0);

-- Insert service types
INSERT INTO `service_type` (`type_name`, `description`, `standard_time`, `price`) VALUES
('Regular Cleaning', 'Standard room cleaning service', 30, 50.00),
('Deep Cleaning', 'Comprehensive deep cleaning including curtains and mattress', 60, 100.00),
('Bed Sheet Change', 'Replace bed sheets and covers', 15, 20.00),
('Express Cleaning', 'Priority handling for quick completion', 20, 80.00),
('Evening Service', 'Evening room tidying', 15, 30.00);

-- Insert inventory items
INSERT INTO `inventory_item` (`item_name`, `category`, `quantity`, `min_stock`, `unit`) VALUES
('Towel', 'Textile', 150, 50, 'piece'),
('Bed Sheet', 'Textile', 80, 30, 'piece'),
('Toothbrush', 'Toiletries', 200, 100, 'piece'),
('Shampoo', 'Toiletries', 45, 50, 'bottle'),
('Body Wash', 'Toiletries', 40, 50, 'bottle'),
('Tissue Paper', 'Cleaning Supplies', 300, 100, 'box'),
('Disinfectant', 'Cleaning Supplies', 25, 20, 'bottle'),
('Trash Bag', 'Cleaning Supplies', 500, 200, 'piece');

-- Insert service orders
INSERT INTO `service_order` (`order_no`, `room_id`, `guest_id`, `service_type_id`, `status`, `priority`, `request_time`, `remarks`) VALUES
('SO20260228001', 1, 2, 1, 3, 0, '2026-02-28 09:00:00', 'Please clean ASAP'),
('SO20260228002', 3, 2, 2, 2, 1, '2026-02-28 10:00:00', 'Need deep cleaning'),
('SO20260228003', 4, 3, 1, 1, 0, '2026-02-28 11:00:00', '');

-- ----------------------------
-- 11. Role Table
-- ----------------------------
DROP TABLE IF EXISTS `role`;
CREATE TABLE `role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_role_name` (`role_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 12. Resource Table
-- ----------------------------
DROP TABLE IF EXISTS `resource`;
CREATE TABLE `resource` (
  `id` int NOT NULL AUTO_INCREMENT,
  `resource_name` varchar(100) DEFAULT NULL,
  `resource_link` varchar(255) DEFAULT NULL,
  `resource_method` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 13. User Role Table
-- ----------------------------
DROP TABLE IF EXISTS `user_role`;
CREATE TABLE `user_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `role_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_role_id` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 14. Role Resource Table
-- ----------------------------
DROP TABLE IF EXISTS `role_resource`;
CREATE TABLE `role_resource` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_id` int NOT NULL,
  `resource_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_role_id` (`role_id`),
  KEY `idx_resource_id` (`resource_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert roles
INSERT INTO `role` (`role_name`) VALUES ('admin'), ('cleaner'), ('guest');

-- Insert resources (API endpoints)
INSERT INTO `resource` (`resource_name`, `resource_link`, `resource_method`) VALUES
('Service Order List', '/api/service-order', 'GET'),
('Service Order Create', '/api/service-order', 'POST'),
('Service Order Update', '/api/service-order/{order_id}', 'PUT'),
('Service Order Delete', '/api/service-order/{order_id}', 'DELETE'),
('Service Order Paginated', '/api/service-order/paginated', 'POST'),
('Assign Staff', '/api/service-order/assign/{order_id}', 'POST'),
('Start Work', '/api/service-order/start/{order_id}', 'POST'),
('Complete Work', '/api/service-order/complete/{order_id}', 'POST'),
('Room List', '/api/room', 'GET'),
('Room Create', '/api/room', 'POST'),
('Room Update', '/api/room/{room_id}', 'PUT'),
('Room Delete', '/api/room/{room_id}', 'DELETE'),
('Room Paginated', '/api/room/paginated', 'POST'),
('User List', '/api/user', 'GET'),
('User Create', '/api/user', 'POST'),
('User Update', '/api/user/{user_id}', 'PUT'),
('User Delete', '/api/user/{user_id}', 'DELETE'),
('Inventory List', '/api/inventory', 'GET'),
('Inventory Create', '/api/inventory', 'POST'),
('Inventory Update', '/api/inventory/{item_id}', 'PUT'),
('Inventory Delete', '/api/inventory/{item_id}', 'DELETE'),
('Inventory Paginated', '/api/inventory/paginated', 'POST'),
('Service Type List', '/api/service-type', 'GET'),
('Wallet', '/api/wallet', 'GET'),
('Wallet Recharge', '/api/wallet/recharge', 'POST');

-- Insert user roles (admin=1, cleaner=2, guest=3)
INSERT INTO `user_role` (`user_id`, `role_id`) VALUES 
(1, 1),  -- admin user -> admin role
(2, 2),  -- cleaner1 -> cleaner role
(3, 2),  -- cleaner2 -> cleaner role
(4, 3);  -- guest1 -> guest role

-- Insert role resources - Admin gets all
INSERT INTO `role_resource` (`role_id`, `resource_id`) 
SELECT 1, id FROM `resource`;

-- Insert role resources - Cleaner gets limited resources
INSERT INTO `role_resource` (`role_id`, `resource_id`) VALUES 
(2, 1),  -- Service Order List
(2, 5),  -- Service Order Paginated
(2, 6),  -- Assign Staff
(2, 7),  -- Start Work
(2, 8),  -- Complete Work
(2, 9),  -- Room List
(2, 13), -- Room Paginated
(2, 24), -- Wallet
(2, 25); -- Wallet Recharge

-- Insert role resources - Guest gets limited resources
INSERT INTO `role_resource` (`role_id`, `resource_id`) VALUES 
(3, 1),  -- Service Order List
(3, 2),  -- Service Order Create
(3, 5),  -- Service Order Paginated
(3, 9),  -- Room List
(3, 13), -- Room Paginated
(3, 24), -- Wallet
(3, 25); -- Wallet Recharge

SET FOREIGN_KEY_CHECKS = 1;
