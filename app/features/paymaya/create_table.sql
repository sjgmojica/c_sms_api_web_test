-- Adminer 4.2.2 MySQL dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

DROP TABLE IF EXISTS `paymaya_checkout`;
CREATE TABLE `paymaya_checkout` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `checkout_id` int(11) NOT NULL,
  `receipt_number` varchar(32) NOT NULL,
  `transaction_reference_number` varchar(128) NOT NULL,
  `paymaya_checkout_id` varchar(128) NOT NULL,
  `status` enum('CREATED','EXPIRED','PROCESSING','COMPLETED') NOT NULL,
  `payment_status` enum('PENDING','AUTH_SUCCESS','AUTH_FAILURE','PAYMENT_SUCCESS','PAYMENT_FAILURE') NOT NULL,
  `date_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- 2016-08-12 08:18:02