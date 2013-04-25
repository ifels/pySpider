
CREATE SCHEMA IF NOT EXISTS `spiderdb` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci 

CREATE  TABLE IF NOT EXISTS `spiderdb`.`tb_video` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `title` VARCHAR(256) NOT NULL ,
  `img` VARCHAR(256) NULL ,
  `sub_title` VARCHAR(512) NULL ,
  `actors` VARCHAR(128) NULL ,
  `director` VARCHAR(128) NULL ,
  `video_type` VARCHAR(45) NULL ,
  `video_language` VARCHAR(45) NULL ,
  `area` VARCHAR(45) NULL ,
  `update_time` VARCHAR(45) NULL ,
  `public_time` VARCHAR(45) NULL ,
  `status` VARCHAR(45) NULL ,
  `brief` VARCHAR(45) NULL ,
  `hast_list` VARCHAR(45) NULL ,
  `ref_url` VARCHAR(45) NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB