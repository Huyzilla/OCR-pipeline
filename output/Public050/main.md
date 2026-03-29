# Public_050

# Khái niệm độ phức tạp thuật toán 

Thời gian thực hiện một giải thuật bằng chương trình máy tính phụ thuộc vào các yếu tố:

  * Kích thước dữ liệu đầu vào: một giải thuật hay một chương trình máy tính thực hiện trên tập dữ liệu có kích thước lớn hiển nhiên mất nhiều thời gian hơn thuật toán hoặc chương trình này thực hiện trên tập dữ liệu đầu vào có kích thước nhỏ.

  * Phần cứng của hệ thống máy tính: hệ thống máy tính có tốc độ cao thực hiện nhanh hơn trên hệ thống máy tính có tốc độ thấp.


Tuy nhiên, nếu ta quan niệm thời gian thực hiện của một thuật toán là số các phép toán sơ cấp thực hiện trong thuật toán đó thì phần cứng máy tính không còn là yếu tố ảnh hưởng đến quá trình xác định thời gian thực hiện của một thuật toán. Với quan niệm này, độ phức tạp thời gian thực hiện của một thuật toán chỉ còn phụ thuộc duy nhất vào độ dài dữ liệu đầu vào.

Gọi độ dài dữ liệu đầu vào là _T_ ( _n_ ). Khi đó, số lượng các phép toán sơ cấp để giải bài toán _P_ thực hiện theo thuật toán _F_ = _F_ 1 _F_ 2.. _F_ n trên độ dài dữ liệu _T_ ( _n_ ) là _F_ ( _T_ ( _n_ )). Để xác định số lượng các phép toán sơ cấp _F_ i ( _i_ = _1_ , _2_ , .., _n_ ) thực hiện trong thuật toán _F_ ta cần phải giải bài toán đếm để xác định _F_ ( _T_ ( _n_ )). Đây là bài toán vô cùng khó và không phải lúc nào cũng giải được []. Để đơn giản điều này, người ta thường tìm đến các phương pháp xấp xỉ để tính toán độ phức tạp thời gian của một thuật toán. Điều này có nghĩa, khi ta không thể xây dựng được công thức đếm _F_ ( _T_ ( _n_ )), nhưng ta lại có khẳng định chắc chắn _F_ ( _T_ ( _n_ )) không vượt quá một phiếm hàm biết trước _G_ ( _n_ ) thì ta nói _F_ ( _T_ ( _n_ )) thực hiện nhanh nhất là _G_ ( _n_ ).

**Tổng quát** , _cho hai hàm f_ ( _x_ ) _, g_ ( _x_ ) _xác định trên tập các số nguyên dương hoặc tập các số thực. Hàm f_ ( _x_ ) _được gọi là O_ ( _g_ ( _x_ )) _nếu tồn tại một hằng số C >0 và n0 sao cho:_

| _f_ ( _x_ )| ≤ _C_.| _g_ ( _x_ )| với mọi _x_ ≥ _n_ 0.

Điều này có nghĩa với các giá trị _x_ ≥ _n_ 0 hàm _f_ ( _x_ ) bị chặn trên bởi hằng số _C_ nhân với _g_ ( _x_ ). Nếu _f_ ( _x_ ) là thời gian thực hiện của một thuật toán thì ta nói giải thuật đó có cấp _g_ ( _x_ ) hay độ phức tạp thuật toán _f_ ( _x_ ) là _O_ ( _g_ ( _x_ )).

**Ghi chú**. Các hằng số _C_ , _n_ 0 thỏa mãn điều kiện trên là không duy nhất. Nếu có đồng thời _f_ ( _x_ ) là _O_ ( _g_ ( _x_ )) và _h_ ( _x_ ) thỏa mãn _g_ ( _x_ ) < _h_ ( _x_ ) với _x_ > _n_ 0 thì ta cũng có _f_ ( _x_ ) là _O_ ( _h_ ( _n_ )).

**Ví dụ 1.6**. Cho 𝑓(𝑥) = 𝑎𝑛𝑥𝑛 \+ 𝑎𝑛−1𝑥𝑛−1 \+ ⋯ + 𝑎1𝑥 + 𝑎0; trong đó, _a_ i là các số thực (i =0,1, 2, ..,n). Khi đó _f_ ( _x_ ) = _O_ ( _x_ n).

**Chứng minh**. Thực vậy, với mọi _x_ > _1_ ta có:

|𝑓(𝑥) = |𝑎𝑛𝑥𝑛 \+ 𝑎𝑛−1𝑥𝑛−1 \+ ⋯ + 𝑎1𝑥 + 𝑎0|

≤ |𝑎𝑛|𝑥𝑛 \+ |𝑎𝑛−1|𝑥𝑛−1 \+ ⋯ \+ |𝑎1|𝑥 + |𝑎0|

≤ |𝑎𝑛|𝑥𝑛 \+ |𝑎𝑛−1|𝑥𝑛 \+ ⋯ + |𝑎1|𝑥𝑛 \+ |𝑎0|𝑥𝑛

≤ 𝑥𝑛(|𝑎𝑛| + |𝑎𝑛−1| + ⋯ + |𝑎1| \+ |𝑎0|)

≤ 𝐶. 𝑥𝑛 = 𝑂(𝑥𝑛) . Trong đó, 𝐶 = (|𝑎𝑛| + |𝑎𝑛−1| + ⋯ + |𝑎1| \+ |𝑎0|).

# Một số quy tắc xác định độ phức tạp thuật toán 

Như đã đề cập ở trên, bản chất của việc xác định độ phức tạp thuật toán là giải bài toán đếm số lượng các phép toán sơ cấp thực hiện trong thuật toán đó. Do vậy, tất cả các phương pháp giải bài toán đếm thông thường đều được áp dụng trong khi xác định độ phức tạp thuật toán. Hai nguyên lý cơ bản để giải bài toán đếm là nguyên lý cộng và nguyên lý nhân cũng được mở rộng trong khi ước lượng độ phức tạp thuật toán.

**Nguyên tắc tổng:** Nếu _f_ 1( _x_ ) có độ phức tạp là O( _g_ 1( _x_ )) và _f_ 2( _x_ ) có độ phức tạp là O( _g_ 2( _x_ )) thì độ phức tạp của ( _f_ 1( _x_ ) + f2( _x_ ) là O( _Max_ ( _g_ 1( _x_ ), _g_ 2( _x_ )).

**Chứng minh**. Vì _f_ 1( _x_ ) có độ phức tạp là O( _g_ 1( _x_ ) nên tồn tại hằng số _C_ 1 và _k_ 1 sao cho | _f_ 1( _x_ )|| _g_ 1( _x_ )| với mọi _x_  _k_ 1. Vì _f_ 2( _x_ ) có độ phức tạp là O( _g_ 2( _x_ )) nên tồn tại hằng số _C_ 2 và _k_ 2 sao cho | _f_ 2( _x_ )|| _g_ 2( _x_ )| với mọi _x_  _k_ 2.

Ta lại có :
| _f_ 1( _x_ )+ _f_ 2( _x_ )|  | _f_ 1( _x_ )| + | _f_ 2( _x_ )|

 _C_ 1| _g_ 1( _x_ )| + _C_ 2| _g_ 2( _x_ )|

 _C_ | _g_ ( _x_ )| với mọi _x_ > _k_ ;

Trong đó, _C_ = _C_ 1 \+ _C_ 2; _g_ ( _x_ ) = _max_ ( _g_ 1( _x_ ), _g_ 2( _x_ )); _k_ = _max_ ( _k_ 1, _k_ 2).

**Tổng quát**. Nếu độ phức tạp của _f_ 1( _x_ ), _f_ 2( _x_ ),.., _f_ m( _x_ ) lần lượt là O( _g_ 1( _x_ )), O( _g_ 2( _x_ )),.., O( _g_ n( _x_ )) thì độ phức tạp của _f_ 1( _x_ ) + _f_ 2( _x_ ) \+ ..+ _f_ m( _x_ ) là O( _max_ ( _g_ 1( _x_ ), _g_ 2( _x_ ),.., _g_ m( _x_ )).

**Nguyên tắc nhân:** Nếu _f_ ( _x_ ) có độ phức tạp là O( _g_ ( _x_ ) thì độ phức tạp của _f_ n( _x_ ) là O( _g_ n( _x_ )). Trong đó:

_f_ n( _x_ ) = _f_ ( _x_ ). _f_ ( _x_ )…. _f_ ( _x_ ). //n lần _f_ ( _x_ ). _g_ n( _x_ ) = _g_ ( _x_ ). _g_ ( _x_ )… _g_ ( _x_ ).// _n_ lần _g_ ( _x_ )

**Chứng minh**. Thật vậy theo giả thiết _f_ ( _x_ ) là O( _g_ ( _x_ )) nên tồn tại hằng số _C_ và _k_ sao cho với mọi _x_ > _k_ thì | _f_ ( _x_ )| C.| _g_ ( _x_ ). Ta có:

|𝑓𝑛(𝑥)| = |𝑓1(𝑥). 𝑓2(𝑥) … 𝑓𝑛(𝑥)|

≤ |𝐶. 𝑔1(𝑥). 𝐶. 𝑔2(𝑥) … 𝐶. 𝑔𝑛(𝑥)|

≤ |𝐶𝑛. 𝑔𝑛(𝑥)| = 𝑂(𝑔𝑛(𝑥))

# Một số dạng hàm được dùng xác định độ phức tạp thuật toán 

Như đã đề cập ở trên, để xác định chính xác độ phức tạp thuật toán f(x) là bài toán

khó nên ta thường xấp xỉ độ phức tạp thuật toán với một phiếm hàm O(g(x)). Dưới đây là

một số phiếm hàm của O(g(x)).

**Bảng 1.1. Các dạng hàm xác định độ phức tạp thuật toán**

![](images/image1.jpg)

**Hình 1.1**. _Độ tăng của các hàm theo độ dài dữ liệu_

Dưới đây là một số qui tắc xác định O(g(x)):

  * Nếu một thuật toán có độ phức tạp hằng số thì thời gian thực hiện thuật toán đó không phụ thuộc vào độ dài dữ liệu.

  * Một thuật toán có độ phức tạp logarit của f(n) thì ta viết O(log(n)) mà không cần chỉ rõ cơ số của phép logarit.

  * Với P(n) là một đa thức bậc k thì O(P(n)) = O(nk).

  * Thuật toán có độ phức tạp đa thức hoặc nhỏ hơn được xem là những thuật toán thực tế có thể thực hiện được bằng máy tính. Các thuật toán có độ phức tạp hàm mũ, hàm giai thừa được xem là những thuật toán thực tế không giải được bằng máy tính.


# Độ phức tạp của các cấu trúc lệnh 

Để đánh giá độ phức tạp của một thuật toán đã được mã hóa thành chương trình máy tính ta thực hiện theo một số qui tắc sau.

**Độ phức tạp hằng số O(1):** đoạn chương trình không chứa vòng lặp hoặc lời gọi đệ qui có tham biến là một hằng số.

**Ví dụ 1.7**. Đoạn chương trình dưới đây có độ phức tạp hằng số. _for_ ( _i=1; i <=c; i++_) {

_< Tập các chỉ thị có độ phức tạp O(1)>;_

}

**Độ phức tạp O(n)** : Độ phức tạp của hàm hoặc đoạn code là O(n) nếu biến trong vòng lặp tăng hoặc giảm bởi mộ hằng số c.

**Ví dụ 1.8**. Đoạn code dưới đây có độ phức tạp hằng số. for (i=1; i<=n; i = i + c ) {

< _Tập các chỉ thị có độ phức tạp O(1)_ >;

}

for (i=n; i>0; i = i - c ){

< _Tập các chỉ thị có độ phức tạp O(1)_ >;

}

**Độ phức tạp đa thức O(n** c **):** Độ phức tạp của _c_ vòng lặp lồng nhau, mỗi vòng lặp đều có độ phức tạp O(n) là **O(n** c **).**

**Ví dụ 1.9**. Đoạn code dưới đây có độ phức tạp O(n2).

for (i=1; i<=n; i = i + c ) { for (j=1; j<=n; j = j + c){

< _Tập các chỉ thị có độ phức tạp O(1)_ >;

}

}

for (i = n; i >0 ; i = i - c ) { for (j = i- 1; j>1; j = j -c ){

< _Tập các chỉ thị có độ phức tạp O(1)_ >;

} }

**Độ phức tạp logarit O(Log(n))** : Độ phức tạp của vòng lặp là log(n) nếu biểu thức khởi đầu lại của vòng lặp được chia hoặc nhân với một hằng số c.

**Ví dụ 1.10**. Đoạn code dưới đây có độ phức tạp Log(n). for (i=1; i <=n; i = i *c ){

< _Tập các chỉ thị có độ phức tạp O(1)_ >;

}

for (j=n; j >0 ; j = j / c ){

< _Tập các chỉ thị có độ phức tạp O(1)_ >;

}

**Độ phức tạp hằng số O(Log (Log(n))):** nếu biểu thức khởi đầu lại của vòng lặp được nhân hoặc chia cho một hàm mũ.

**Ví dụ 1.11**. Đoạn code dưới đây có độ phức tạp Log Log(n). for (i=1; j<=n; j*= Pow(i, c) ){

< _Tập các chỉ thị có độ phức tạp O(1)_ >;

}

for (j=n; j>=0; j = j- Function(j) ){ //Function(j) =sqrt(j) hoặc lớn hơn 2.

< _Tập các chỉ thị có độ phức tạp O(1)_ >;

}

**Độ phức tạp của chương trình** : độ phức tạp của một chương trình bằng số lần thực hiện một chỉ thị tích cực trong chương trình đó. Trong đó, một chỉ thị được gọi là tích cực trong chương trình nếu chỉ thị đó phụ thuộc vào độ dài dữ liệu và thực hiện không ít hơn bất kỳ một chỉ thị nào khác trong chương trình.

**Ví dụ 1.12**. Tìm độ phức tạp thuật toán sắp xếp kiểu Bubble-Sort? Void Bubble-Sort ( int A[], int n ) {

for ( i=1; i<n; i++) { for ( j = i+1; j<=n; j++){ if (A[i] > A[j]) {// _đây chính là chỉ thị tích cực_ t = A[i]; A[i] = A[j]; A[j] = t;

}

}

}

}

**Lời giả** i. Sử dụng trực tiếp nguyên lý cộng ta có:

  * Với i =1 ta cần sử dụng n-1 phép so sánh A[i] với A[j];

  * Với i = 2 ta cần sử dụng n-2 phép so sánh A[i] với A[j];

  * . . . . .

  * Với i = n-1 ta cần sử dụng 1 phép so sánh A[i] với A[j]; Vì vậy tổng số các phép toán cần thực hiện là:


S = (n-1) + (n-2) + . . . + 2 + 1 = n(n-1)/2 n2 = O(n2).

**Ghi chú**. Độ phức tạp thuật toán cũng là số lần thực hiện phép toán tích cực. Phép toán tích cực là phép toán thực hiện nhiều nhất đối với thuật toán.

# Quy trình giải quyết bài toán trên máy tính 

Để giải quyết một bài toán hoặc vấn đề trong tin học ta thực hiện thông qua 6 bước như sau:

**Bước 1. Xác định yêu cầu bài toán.** Xem xét bài toán cần xử lý vấn đề gì? Giả thiết nào đã được biết trước và lời giải cần đạt những yêu cầu gì? Ví dụ thời gian, hay không gian nhớ.

**Bước 2. Tìm cấu trúc dữ liệu thích hợp biểu diễn các đối tượng cần xử lý của bài toán.** Cấu trúc dữ liệu phải biểu diễn đầy đủ các đối tượng thông tin vào của bài toán. Các thao tác trên cấu trúc dữ liệu phải phù hợp với những thao tác của thuật toán được lựa chọn. Cấu trúc dữ liệu phải cài đặt được bằng ngôn ngữ lập trình cụ thể đáp ứng yêu cầu bài toán.

**Bước 3. Lựa chọn thuật toán.** Thuật toán phải đáp ứng được yêu của bài toán và phù hợp với cấu trúc dữ liệu đã được lựa chọn Bước 1.

**Bước 4. Cài đặt thuật toán.** Thuật toán cần được cài đặt bằng một ngôn ngữ lập trình cụ thể. Ngôn ngữ lập trình sử dụng phải có các cấu trúc dữ liệu đã lựa chọn.

**Bước 5. Kiểm thử chương trình.** Thử nghiệm thuật toán (chương trình) trên các bộ dữ liệu thực. Các bộ dữ liệu cần phải bao phủ lên tất cả các trường hợp của thuật toán.

**Bước 6. Tối ưu chương trìn** h: Cải tiến để chương trình tốt hơn.

.