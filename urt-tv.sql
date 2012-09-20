-- phpMyAdmin SQL Dump
-- version 3.3.7deb7
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Erstellungszeit: 20. September 2012 um 23:45
-- Server Version: 5.1.61
-- PHP-Version: 5.3.15-1~dotdeb.0

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Datenbank: `1_urt-tv`
--

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `betting`
--

CREATE TABLE IF NOT EXISTS `betting` (
  `ID` text NOT NULL,
  `TeamA` text NOT NULL,
  `TeamB` text NOT NULL,
  `Draw` text NOT NULL,
  `Total` text NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `betting_host`
--

CREATE TABLE IF NOT EXISTS `betting_host` (
  `ID` text NOT NULL,
  `host` text NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `clanalias`
--

CREATE TABLE IF NOT EXISTS `clanalias` (
  `Clan` text NOT NULL,
  `Alias` text NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `gtv`
--

CREATE TABLE IF NOT EXISTS `gtv` (
  `ID` varchar(3) NOT NULL,
  `TeamA` text NOT NULL,
  `TeamB` text NOT NULL,
  `Date` text NOT NULL,
  `Time` text NOT NULL,
  `Type` text NOT NULL,
  `Score` varchar(5) NOT NULL DEFAULT '0-0',
  `IP` text NOT NULL,
  `Demo` text NOT NULL,
  `Done` varchar(3) NOT NULL DEFAULT 'no',
  `League` text NOT NULL,
  `Month` text NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `gtv_new`
--

CREATE TABLE IF NOT EXISTS `gtv_new` (
  `ID` text NOT NULL,
  `TeamA` text NOT NULL,
  `TeamB` text NOT NULL,
  `Date` text NOT NULL,
  `Time` text NOT NULL,
  `League` text NOT NULL,
  `Type` text NOT NULL,
  `Who` text NOT NULL,
  `Server` text NOT NULL,
  `Public` varchar(3) NOT NULL DEFAULT 'no',
  `Done` varchar(3) NOT NULL DEFAULT 'no',
  `Score` text NOT NULL,
  `Demo` text NOT NULL,
  `Month` text NOT NULL,
  `Spam` text NOT NULL,
  `Shoutcast` text NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `gtv_sc`
--

CREATE TABLE IF NOT EXISTS `gtv_sc` (
  `ID` text,
  `TeamA` text NOT NULL,
  `TeamB` text NOT NULL,
  `Date` text NOT NULL,
  `Time` text NOT NULL,
  `League` text NOT NULL,
  `Type` text NOT NULL,
  `Who` text NOT NULL,
  `Server` text NOT NULL,
  `Public` varchar(3) NOT NULL DEFAULT 'no',
  `Done` varchar(3) NOT NULL DEFAULT 'no',
  `Score` text NOT NULL,
  `Demo` text NOT NULL,
  `Month` text NOT NULL,
  `Spam` text NOT NULL,
  `Stream` text NOT NULL,
  `Streamer` text NOT NULL,
  `Shoutcaster` text NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `gtv_test`
--

CREATE TABLE IF NOT EXISTS `gtv_test` (
  `ID` text NOT NULL,
  `TeamA` text NOT NULL,
  `TeamB` text NOT NULL,
  `Date` text NOT NULL,
  `Time` text NOT NULL,
  `League` text NOT NULL,
  `Type` text NOT NULL,
  `Who` text NOT NULL,
  `Server` text NOT NULL,
  `Public` varchar(3) NOT NULL DEFAULT 'no',
  `Done` varchar(3) NOT NULL DEFAULT 'no',
  `Score` text NOT NULL,
  `Demo` text NOT NULL,
  `Month` text NOT NULL,
  `Spam` text NOT NULL,
  `Stream` text NOT NULL,
  `Streamer` text NOT NULL,
  `Shoutcaster` text NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `screens`
--

CREATE TABLE IF NOT EXISTS `screens` (
  `ID` int(11) NOT NULL,
  `ss` varchar(40) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `servers`
--

CREATE TABLE IF NOT EXISTS `servers` (
  `ID` int(11) NOT NULL,
  `IP` text NOT NULL,
  `Admin` text NOT NULL,
  `Camera` text NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `status_new`
--

CREATE TABLE IF NOT EXISTS `status_new` (
  `Name` text NOT NULL,
  `Status` text NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
