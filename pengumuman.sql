-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Feb 20, 2022 at 03:40 PM
-- Server version: 10.4.22-MariaDB
-- PHP Version: 8.1.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pengumuman`
--

-- --------------------------------------------------------

--
-- Table structure for table `isi_pengumuman`
--

CREATE TABLE `isi_pengumuman` (
  `id_pengumuman` int(11) NOT NULL,
  `id_user` int(11) NOT NULL,
  `isi` longtext NOT NULL,
  `jurusan` int(11) NOT NULL,
  `prodi` int(11) NOT NULL,
  `tingkat` int(11) NOT NULL,
  `tanggal` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `isi_pengumuman`
--

INSERT INTO `isi_pengumuman` (`id_pengumuman`, `id_user`, `isi`, `jurusan`, `prodi`, `tingkat`, `tanggal`) VALUES
(3079, 1201809639, 'HELOW WORLD', 1, 1, 1, '2022-02-20 14:38:00'),
(5610, 1201809639, 'NEW UPDATE', 1, 1, 1, '2022-01-16 12:41:00'),
(7711, 1201809639, 'ANJAYYYY', 1, 1, 1, '2022-01-16 12:38:00');

-- --------------------------------------------------------

--
-- Table structure for table `jurusan`
--

CREATE TABLE `jurusan` (
  `id_jur` int(11) NOT NULL,
  `nama_jur` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `jurusan`
--

INSERT INTO `jurusan` (`id_jur`, `nama_jur`) VALUES
(1, 'D4'),
(2, 'D3');

-- --------------------------------------------------------

--
-- Table structure for table `prodi`
--

CREATE TABLE `prodi` (
  `id_prodi` int(11) NOT NULL,
  `nama_prod` text NOT NULL,
  `spp` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `prodi`
--

INSERT INTO `prodi` (`id_prodi`, `nama_prod`, `spp`) VALUES
(1, 'Teknik Informatika', 7600000),
(2, 'Sistem Informasi', 7000000);

-- --------------------------------------------------------

--
-- Table structure for table `reminder_user`
--

CREATE TABLE `reminder_user` (
  `id_reminder` int(11) NOT NULL,
  `id_telegram` bigint(11) NOT NULL,
  `isi_reminder` varchar(255) NOT NULL,
  `waktu` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `reminder_user`
--

INSERT INTO `reminder_user` (`id_reminder`, `id_telegram`, `isi_reminder`, `waktu`) VALUES
(2134, 5048963027, 'sidang proyek', '2022-02-20 06:41:00'),
(3151, 1201809639, 'mabar', '2022-12-12 21:10:00'),
(5143, 1201809639, 'anjay update', '2022-01-16 04:36:00'),
(7335, 1201809639, 'mabar valorant', '2022-01-13 01:30:00'),
(9866, 1201809639, 'valorant yok', '2022-01-16 04:41:00');

-- --------------------------------------------------------

--
-- Table structure for table `siswa`
--

CREATE TABLE `siswa` (
  `id_tele` bigint(20) NOT NULL,
  `nama` varchar(255) NOT NULL,
  `jurusan` int(11) NOT NULL,
  `prodi` int(11) NOT NULL,
  `tingkat` int(11) NOT NULL,
  `paid_tuition` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `siswa`
--

INSERT INTO `siswa` (`id_tele`, `nama`, `jurusan`, `prodi`, `tingkat`, `paid_tuition`) VALUES
(1201809639, 'Jose Chasey Pratama', 1, 1, 1, 5000000),
(1205773292, 'Will', 1, 1, 1, 7600000),
(1402911915, 'HANAN', 1, 1, 1, 3000000),
(5048963027, 'Yarsya Fariz', 1, 1, 1, 100000);

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id_tele` int(11) NOT NULL,
  `nama` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id_tele`, `nama`) VALUES
(1201809639, 'Jose'),
(1205773292, 'WIl');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `isi_pengumuman`
--
ALTER TABLE `isi_pengumuman`
  ADD PRIMARY KEY (`id_pengumuman`),
  ADD KEY `FK JURUSAN` (`jurusan`),
  ADD KEY `FK PRODI` (`prodi`),
  ADD KEY `FK USER` (`id_user`);

--
-- Indexes for table `jurusan`
--
ALTER TABLE `jurusan`
  ADD PRIMARY KEY (`id_jur`);

--
-- Indexes for table `prodi`
--
ALTER TABLE `prodi`
  ADD PRIMARY KEY (`id_prodi`);

--
-- Indexes for table `reminder_user`
--
ALTER TABLE `reminder_user`
  ADD PRIMARY KEY (`id_reminder`);

--
-- Indexes for table `siswa`
--
ALTER TABLE `siswa`
  ADD PRIMARY KEY (`id_tele`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id_tele`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `isi_pengumuman`
--
ALTER TABLE `isi_pengumuman`
  ADD CONSTRAINT `FK JURUSAN` FOREIGN KEY (`jurusan`) REFERENCES `jurusan` (`id_jur`),
  ADD CONSTRAINT `FK PRODI` FOREIGN KEY (`prodi`) REFERENCES `prodi` (`id_prodi`),
  ADD CONSTRAINT `FK USER` FOREIGN KEY (`id_user`) REFERENCES `user` (`id_tele`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
