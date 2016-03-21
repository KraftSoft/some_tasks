-- MySQL dump 10.13  Distrib 5.5.47, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: fs_prototype
-- ------------------------------------------------------
-- Server version	5.6.28-0ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
INSERT INTO `groups` VALUES (1,'admins');
/*!40000 ALTER TABLE `groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `meta`
--

DROP TABLE IF EXISTS `meta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `meta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date_create` datetime NOT NULL,
  `last_modify` datetime NOT NULL,
  `owner_id` int(11) NOT NULL,
  `last_changer_id` int(11) NOT NULL,
  `path` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `path_UNIQUE` (`path`),
  KEY `fk_meta_1_idx` (`owner_id`),
  KEY `fk_meta_2_idx` (`last_changer_id`),
  CONSTRAINT `fk_meta_1` FOREIGN KEY (`owner_id`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_meta_2` FOREIGN KEY (`last_changer_id`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meta`
--

LOCK TABLES `meta` WRITE;
/*!40000 ALTER TABLE `meta` DISABLE KEYS */;
INSERT INTO `meta` VALUES (1,'2016-03-20 00:00:00','2016-03-20 00:00:00',1,1,'/'),(13,'2016-03-21 10:30:31','2016-03-21 10:30:31',1,1,'/index.html'),(14,'2016-03-21 10:30:42','2016-03-21 10:30:42',1,1,'/media'),(15,'2016-03-21 10:36:20','2016-03-21 10:36:20',1,1,'/media/my'),(16,'2016-03-21 10:36:45','2016-03-21 10:36:45',1,1,'/media/my/i_am.jpg'),(17,'2016-03-21 10:37:05','2016-03-21 10:37:05',1,1,'/media/my/i_and_my_cat.jpg'),(18,'2016-03-21 10:38:07','2016-03-21 10:38:07',1,1,'/media/my/my_sicret_photo.jpg'),(19,'2016-03-21 10:44:24','2016-03-21 10:44:24',1,1,'/media/sicret_folder'),(20,'2016-03-21 10:44:46','2016-03-21 10:44:46',1,1,'/media/sicret_folder/sicret_doc.txt'),(21,'2016-03-21 10:50:50','2016-03-21 10:50:50',1,1,'/root_dir'),(22,'2016-03-21 10:51:16','2016-03-21 10:51:16',1,1,'/root_dir/root_doc.txt'),(23,'2016-03-21 10:59:25','2016-03-21 10:59:25',1,1,'/root_folder');
/*!40000 ALTER TABLE `meta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `node`
--

DROP TABLE IF EXISTS `node`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `node` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` tinyint(4) NOT NULL COMMENT '0 - file\n1 - directory',
  `meta_id` int(11) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `name` varchar(255) CHARACTER SET latin1 NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_node_1_idx` (`parent_id`),
  CONSTRAINT `fk_node_1` FOREIGN KEY (`parent_id`) REFERENCES `node` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `node`
--

LOCK TABLES `node` WRITE;
/*!40000 ALTER TABLE `node` DISABLE KEYS */;
INSERT INTO `node` VALUES (1,1,1,NULL,'/'),(12,0,13,1,'index.html'),(13,1,14,1,'media'),(14,1,15,13,'my'),(15,0,16,14,'i_am.jpg'),(16,0,17,14,'i_and_my_cat.jpg'),(17,0,18,14,'my_sicret_photo.jpg'),(18,1,19,13,'sicret_folder'),(19,0,20,18,'sicret_doc.txt'),(20,1,21,1,'root_dir'),(21,0,22,20,'root_doc.txt'),(22,1,23,1,'root_folder');
/*!40000 ALTER TABLE `node` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET latin1 DEFAULT NULL,
  `owner_permission` enum('0','1','2','3','4','5','6','7') CHARACTER SET latin1 NOT NULL,
  `group_permission` enum('0','1','2','3','4','5','6','7') CHARACTER SET latin1 NOT NULL,
  `others_permission` enum('0','1','2','3','4','5','6','7') CHARACTER SET latin1 NOT NULL,
  `node_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `node_id_UNIQUE` (`node_id`),
  CONSTRAINT `fk_permissions_1` FOREIGN KEY (`node_id`) REFERENCES `node` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
INSERT INTO `permissions` VALUES (1,'root directory','5','5','5',1),(11,'//index.html file permissions','7','5','5',12),(12,'//media directory permissions','7','5','5',13),(13,'/media/my directory permissions','7','5','5',14),(14,'/media/my/i_am.jpg file permissions','7','5','5',15),(15,'/media/my/i_and_my_cat.jpg file permissions','7','5','5',16),(16,'/media/my/my_sicret_photo.jpg file permissions','7','1','1',17),(17,'/media/sicret_folder directory permissions','7','5','5',18),(18,'/media/sicret_folder/sicret_doc.txt file permissions','7','5','5',19),(19,'/root_dir directory permissions','7','5','5',20),(20,'/root_dir/root_doc.txt file permissions','7','5','5',21),(21,'/root_folder directory permissions','7','1','1',22);
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `login` varchar(32) NOT NULL,
  `password` varchar(128) CHARACTER SET latin1 NOT NULL,
  `group_id` int(11) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`login`),
  KEY `fk_user_1_idx` (`group_id`),
  CONSTRAINT `fk_user_1` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'root','21232f297a57a5a743894a0e4a801fc3',NULL,1),(2,'yandex_user','5795159a1ed7735e162b4e0a5c621352',NULL,0);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-03-21 12:29:11
