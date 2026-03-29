# Public_119

# Giới thiệu

Trong hai bài viết trước, PCA (unsupervised) giữ lại tổng phương sai lớn nhất nhưng không dùng nhãn. Trong phân lớp (supervised), tận dụng nhãn thường cho kết quả tốt hơn. Ví dụ chiếu lên các hướng d1 (gần PC1) và d2 (gần thành phần phụ): d1 có thể làm hai lớp chồng lấn, trong khi d2 tách tốt hơn cho classification. Điều này cho thấy giữ lại nhiều phương sai nhất không phải lúc nào cũng tốt cho phân lớp. LDA ra đời để tìm phép chiếu tuyến tính (projection matrix) tối đa hóa khả năng phân biệt (discriminant). Với C lớp, số chiều mới không vượt quá C−1.

# LDA cho bài toán với 2 classes

## Ý tưởng cơ bản

Discriminant tốt khi: (i) mỗi lớp tập trung (within-class variance nhỏ), (ii) các lớp cách xa nhau (between-class variance lớn).

## Xây dựng hàm mục tiêu

_Ký hiệu: dữ liệu x_n, phép chiếu y_n = w^T x_n._

Kỳ vọng mỗi lớp: m_k = (1/N_k) ∑_{n∈C_k} x_n, k=1,2. (1)

Hiệu kỳ vọng sau chiếu: m_1 − m_2 ⇒ w^T(m_1−m_2). (2)

Within-class variances (không lấy trung bình): s_k^2 = ∑_{n∈C_k} (y_n − m_k)^2. (3)

Ma trận between-class: S_B = (m_1−m_2)(m_1−m_2)^T. (5)

Ma trận within-class: S_W = ∑_{k=1}^2 ∑_{n∈C_k} (x_n−m_k)(x_n−m_k)^T. (6)

**Hàm mục tiêu Fisher (2 lớp):**

J(w) = (w^T S_B w) / (w^T S_W w). (4,7)

## Nghiệm tối ưu (Fisher’s linear discriminant)

_Đạo hàm và sắp xếp lại:_

S_W^{-1} S_B w = J(w) w. (10)

**Chọn nghiệm tỷ lệ:**

w = α S_W^{-1}(m_1 − m_2), α≠0. (11)

# LDA cho multi-class classification

Phép chiếu tuyến tính: y = W^T x, W ∈ R^{D×D′}. Không dùng bias.

**Within-class tổng quát:**

s_W = trace(W^T S_W W), với S_W = ∑_{k=1}^C ∑_{n∈C_k} (x_n − m_k)(x_n − m_k)^T. (17–19)

**Between-class tổng quát:**

s_B = trace(W^T S_B W), với S_B = ∑_{k=1}^C N_k (m_k − m)(m_k − m)^T. (21–22)

**Hàm mục tiêu multi-class:**

J(W) = trace(W^T S_B W) / trace(W^T S_W W).

_Điều kiện tối ưu bậc nhất:_

S_W^{-1} S_B W = J W. (24)

_Các cột của W là các eigenvectors ứng với các trị riêng lớn nhất của S_W^{-1} S_B._

_Bổ đề: rank(S_B) ≤ C − 1 ⇒ số chiều tối đa sau LDA ≤ C − 1._

# Ví dụ nhanh (Python, phác thảo)

_• Tạo dữ liệu 2 lớp: X0, X1 ∈ R^{N×D}; tính m0, m1._

_• S_B = (m0 − m1)(m0 − m1)^T; S_W = ∑ (x − m_k)(x − m_k)^T._

_• W từ eigenvectors của inv(S_W) @ S_B; so sánh sklearn.discriminant_analysis.LDA._

# Thảo luận

LDA là phương pháp supervised giảm chiều và/hoặc phân lớp: tối ưu small within-class & large between-class. Số chiều tối đa sau LDA là ≤ C−1. Giả định thường gặp: phân phối gần Gaussian, các ma trận hiệp phương sai giữa các lớp gần nhau. LDA tốt khi các lớp gần linearly separable; kém hiệu quả nếu không tách tuyến tính.