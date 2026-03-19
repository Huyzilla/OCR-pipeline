# Public_117

# Random variables

Một biến ngẫu nhiên (random variable) x là một đại lượng dùng để đo những đại lượng không xác định. Biến này có thể ký hiệu kết quả/đầu ra (outcome) của một thí nghiệm (ví dụ như tung đồng xu) hoặc một đại lượng biến đổi trong tự nhiên (ví dụ như nhiệt độ trong ngày). Nếu chúng ta quan sát rất nhiều đầu ra {x_i}_{i=1}^I của các thí nghiệm này, ta có thể nhận được những giá trị khác nhau ở mỗi thí nghiệm. Tuy nhiên, sẽ có những giá trị xảy ra nhiều lần hơn những giá trị khác. Thông tin về đầu ra được đo bởi phân phối xác suất (probability distribution) p(x) của biến ngẫu nhiên.  
  
Một biến ngẫu nhiên có thể là rời rạc (discrete) hoặc liên tục (continuous). Một biến ngẫu nhiên rời rạc sẽ lấy giá trị trong một tập hợp cho trước. Ví dụ tung đồng xu thì có hai khả năng là head và tail (tên gọi này bắt nguồn từ đồng xu Mỹ, một mặt có hình mặt người, được gọi là head, trái ngược với mặt này được gọi là mặt tail, cách gọi này hay hơn cách gọi xấp ngửa vì ta không có quy định rõ ràng thế nào là xấp ngay ngửa). Tập các giá trị này có thể là có thứ tự (khi tung xúc xắc) hoặc không có thứ tự (unordered), ví dụ khi đầu ra là các giá trị nắng, mưa, bão, etc. Mỗi đầu ra có một giá trị xác suất tương ứng với nó. Các giá trị xác suất này không âm và có tổng bằng một:

_if x is discrete:_

∑_x p(x) = 1 (1)

Biến ngẫu nhiên liên tục lấy các giá trị là tập con của các số thực. Những giá trị này có thể là hữu hạn, ví dụ thời gian làm bài của mỗi thí sinh trong một bài thi 180 phút, hoặc vô hạn, ví dụ thời gian để chiếc xe bus tiếp theo tới. Không như biến ngẫu nhiên rời rạc, xác suất để đầu ra bằng chính xác một giá trị nào đó, theo lý thuyết, là bằng 0. Thay vào đó, ta có thể hình dung xác suất để đầu ra nằm trong một khoảng giá trị nào đó; và việc này được mô tả bởi hàm mật độ xác suất (probability density function - pdf). Hàm mật độ xác suất luôn cho giá trị dương, và tích phân của nó trên toàn miền possible outcome phải bằng 1.

_if x is continuous:_

∫ p(x) dx = 1 (2)

Để giảm thiểu ký hiệu, hàm mật độ xác suất của một biến ngẫu nhiên liên tục x cũng được ký hiệu là p(x).  
  
Chú ý: Nếu x là biến ngẫu nhiên rời rạc, p(x) luôn luôn nhỏ hơn hoặc bằng 1. Trong khi đó, nếu x là biến ngẫu nhiên liên tục, p(x) có thể nhận giá trị dương bất kỳ, điều này vẫn đảm bảo là tích phân của hàm mật độ xác suất theo toàn bộ giá trị có thể có của x bằng 1. Với biến ngẫu nhiên rời rạc, p(x) được hiểu là mật độ xác suất tại x.

# Joint probability

Xét hai biến ngẫu nhiên x và y. Nếu ta quan sát rất nhiều cặp đầu ra của x và y, thì có những tổ hợp hai đầu ra xảy ra thường xuyên hơn những tổ hợp khác. Thông tin này được biểu diễn bằng một phân phối được gọi là joint probability của x và y, và được viết là p(x, y). Dấu phẩy trong p(x, y) có thể đọc là và, vậy p(x, y) là xác suất của x và y. x và y có thể là hai biến ngẫu nhiên rời rạc, liên tục, hoặc một rời rạc, một liên tục. Luôn nhớ rằng tổng các xác suất trên mọi cặp giá trị có thể xảy ra (x, y) bằng 1.

both are discrete: ∑_{x,y} p(x, y) = 1

both are continuous: ∫∫ p(x, y) dx dy = 1

x is discrete, y is continuous: ∑_x ∫ p(x, y) dy = ∫ (∑_x p(x, y)) dy = 1

Thông thường, chúng ta sẽ làm việc với các bài toán ở đó joint probability xác định trên nhiều hơn 2 biến ngẫu nhiên. Chẳng hạn, p(x, y, z) thể hiện joint probability của 3 biến ngẫu nhiên x, y và z. Khi có nhiều biến ngẫu nhiên, ta có thể viết chúng dưới dạng vector. Ta có thể viết p(x) để thể hiện joint probability của biến ngẫu nhiên nhiều chiều x = [x1, x2, …, xn]^T. Khi có nhiều tập các biến ngẫu nhiên, ví dụ x và y, ta có thể viết p(x, y) để thể hiện joint probability của tất cả các thành phần trong hai biến ngẫu nhiên nhiều chiều này.

# Marginalization

Nếu biết joint probability của nhiều biến ngẫu nhiên, ta cũng có thể xác định được phân bố xác suất của từng biến bằng cách lấy tổng (rời rạc) hoặc tích phân (liên tục) theo tất cả các biến còn lại:

p(x) = ∑_y p(x, y) (3)

p(y) = ∑_x p(x, y) (4)

Và với biến liên tục:

p(x) = ∫ p(x, y) dy (5)

p(y) = ∫ p(x, y) dx (6)

Với nhiều biến hơn, chẳng hạn 4 biến rời rạc x, y, z, w:

p(x) = ∑_{y,z,w} p(x, y, z, w) (7)

p(x, y) = ∑_{z,w} p(x, y, z, w) (8)

Từ đây trở đi, nếu không nói gì thêm, tôi sẽ dùng ký hiệu ∑ để chỉ chung cho cả hai loại biến. Nếu biến ngẫu nhiên là liên tục, bạn đọc ngầm hiểu rằng dấu ∑ cần được thay bằng dấu tích phân ∫, biến lấy vi phân chính là biến được viết dưới dấu ∑.

# Conditional probability

Xác suất có điều kiện (conditional probability) của một biến ngẫu nhiên x biết rằng biến ngẫu nhiên y có giá trị y* được ký hiệu là p(x | y = y*). Conditional probability p(x | y = y*) có thể được tính dựa trên joint probability p(x, y).

p(x | y = y*) = p(x, y = y*) / ∑_x p(x, y = y*) = p(x, y = y*) / p(y = y*) (9)

Thông thường, viết gọn: p(x | y) = p(x, y) / p(y) (10)

Tương tự: p(y | x) = p(y, x) / p(x)

Quan hệ: p(x, y) = p(x | y) p(y) = p(y | x) p(x) (11)

Khi có nhiều hơn hai biến:

p(x, y, z, w) = p(x, y, z | w) p(w) (12)

= p(x, y | z, w) p(z, w) = p(x, y | z, w) p(z | w) p(w) (13)

= p(x | y, z, w) p(y | z, w) p(z | w) p(w) (14)

# Quy tắc Bayes

Từ (11): p(y | x) p(x) = p(x | y) p(y) ⇒ p(y | x) = p(x | y) p(y) / p(x) (15)

= p(x | y) p(y) / ∑_y p(x, y) (16)

= p(x | y) p(y) / ∑_y p(x | y) p(y) (17)

Ba công thức (15)–(17) thường được gọi là Quy tắc Bayes (Bayes’ rule).

# Independence

Nếu x và y độc lập: p(x | y) = p(x) (18), p(y | x) = p(y) (19)

Khi đó: p(x, y) = p(x) p(y) (20)

# Kỳ vọng

Kỳ vọng (expectation) của một biến ngẫu nhiên:

E[x] = ∑_x x p(x) nếu x rời rạc (21)

E[x] = ∫ x p(x) dx nếu x liên tục (22)

Với hàm f(.): E[f(x)] = ∑_x f(x) p(x) (23)

Với joint probability: E[f(x, y)] = ∑_{x,y} f(x, y) p(x, y) (24)

Ba quy tắc:

E[α] = α (25)

E[αx] = α E[x] (26); E[f(x) + g(x)] = E[f(x)] + E[g(x)] (27)

Nếu x, y độc lập: E[f(x) g(y)] = E[f(x)] E[g(y)] (28)

# Một vài phân phối thường gặp

## Bernoulli distribution

Bernoulli distribution: x ∈ {0,1}, tham số λ ∈ [0,1] là xác suất để x=1.

p(x=1) = λ, p(x=0) = 1 − λ

Viết gọn: p(x) = λ^x (1 − λ)^{1 − x} (29)

Ký hiệu: p(x) = Bern_x[λ] (30)

## Categorical distribution

Categorical distribution với K lớp, tham số λ = [λ1, …, λK], ∑_k λk = 1.

p(x = k) = λ_k; viết gọn: p(x) = Cat_x[λ]

Biểu diễn one-hot: x ∈ {e1, …, eK}

p(x = e_k) = ∏_{j=1}^K λ_j^{x_j} = λ_k (31)

## Univariate normal distribution

p(x) = 1 / √(2πσ^2) · exp(− (x − μ)^2 / (2σ^2)) (32)

Ký hiệu: p(x) = Norm_x[μ, σ^2]

## Multivariate normal distribution

p(x) = 1 / ((2π)^{D/2} |Σ|^{1/2}) · exp(−1/2 (x−μ)^T Σ^{−1} (x−μ)) (33)

Ký hiệu: p(x) = Norm_x[μ, Σ]

## Beta distribution

p(λ) = Γ(α+β) / (Γ(α) Γ(β)) · λ^{α−1} (1−λ)^{β−1} (34)

Trong đó Γ(z) = ∫_0^∞ t^{z−1} exp(−t) dt, và Γ[z] = (z−1)! nếu z là số tự nhiên.

Ký hiệu: p(λ) = Beta_λ[α, β]

## Dirichlet distribution

p(λ1, …, λK) = Γ(∑_{k=1}^K α_k) / ∏_{k=1}^K Γ(α_k) · ∏_{k=1}^K λ_k^{α_k−1} (35)

Ký hiệu: p(λ1, …, λK) = Dir_{λ1,…,λK}[α1, …, αK]

# Thảo luận

Về Xác suất thống kê, còn rất nhiều điều cần lưu ý. Tạm thời, phần này ôn tập lại các kiến thức xác suất cơ bản để phục vụ cho các bài viết tiếp theo. Khi nào có phần nào cần nhắc lại, sẽ tiếp tục ôn tập bổ sung.