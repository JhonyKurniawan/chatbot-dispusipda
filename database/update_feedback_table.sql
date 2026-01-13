-- =====================================================
-- UPDATE FEEDBACK TABLE - Perbaikan struktur tabel
-- =====================================================
-- Jalankan script ini di phpMyAdmin atau MySQL CLI
-- untuk update struktur tabel feedback yang sudah ada
-- =====================================================

-- 1. Hapus kolom yang tidak perlu
ALTER TABLE `feedback` DROP COLUMN IF EXISTS `session_id`;
ALTER TABLE `feedback` DROP COLUMN IF EXISTS `message_id`;

-- 2. Tambah kolom baru (jika belum ada)
-- ALTER TABLE `feedback` ADD COLUMN `faq_id` INT(11) DEFAULT NULL AFTER `id`;
-- ALTER TABLE `feedback` ADD COLUMN `is_helpful` TINYINT(1) DEFAULT NULL AFTER `rating`;

-- 3. Tambah index untuk performa query
-- ALTER TABLE `feedback` ADD INDEX `idx_faq_id` (`faq_id`);
-- ALTER TABLE `feedback` ADD INDEX `idx_is_helpful` (`is_helpful`);

-- 4. Tambah foreign key ke tabel faqs (opsional)
-- ALTER TABLE `feedback` ADD CONSTRAINT `feedback_ibfk_faq` FOREIGN KEY (`faq_id`) REFERENCES `faqs` (`id`) ON DELETE SET NULL;

-- =====================================================
-- MIGRATE DATA LAMA - Update faq_id dan is_helpful dari data yang sudah ada
-- =====================================================

-- Update faq_id dari feedback_text yang format "FAQ ID: XXX"
UPDATE feedback 
SET faq_id = CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(feedback_text, 'FAQ ID: ', -1), ' ', 1) AS UNSIGNED)
WHERE faq_id IS NULL AND feedback_text LIKE '%FAQ ID:%';

-- Update is_helpful berdasarkan rating
UPDATE feedback 
SET is_helpful = CASE WHEN rating >= 4 THEN 1 ELSE 0 END
WHERE is_helpful IS NULL;

-- =====================================================
-- SELESAI! Struktur tabel feedback sekarang:
-- - id: Primary key
-- - faq_id: ID FAQ yang di-feedback (untuk tracking)
-- - rating: 5 = helpful, 1 = not helpful
-- - is_helpful: 1 = helpful, 0 = not helpful
-- - feedback_text: 'Helpful' atau 'Not Helpful'
-- - created_at: Waktu feedback
-- =====================================================

-- Query untuk melihat FAQ yang perlu diperbaiki:
-- SELECT f.id, f.question, 
--        SUM(CASE WHEN fb.is_helpful = 1 THEN 1 ELSE 0 END) as helpful,
--        SUM(CASE WHEN fb.is_helpful = 0 THEN 1 ELSE 0 END) as not_helpful
-- FROM faqs f
-- LEFT JOIN feedback fb ON f.id = fb.faq_id
-- GROUP BY f.id
-- HAVING not_helpful > 0
-- ORDER BY not_helpful DESC;
