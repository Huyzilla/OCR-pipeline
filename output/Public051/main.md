# Public_051

Nội dung chính của chương trình bày một số lược đồ thuật toán kinh điển dùng để giải lớp các bài toán liệt kê, bài toán đếm, và bài toán tối ưu và bài toán tồn tại. Mỗi lược đồ thuật toán giải quyết một lớp các bài toán thỏa mãn một số tính chất nào đó. Đây là những lược đồ thuật toán quan trọng nhằm giúp người học vận dụng nó trong khi giải quyết các vấn đề trong tin học. Các lược đồ thuật toán được trình bày trong chương này bao gồm: thuật toán sinh, thuật toán đệ qui, thuật toán quay lui, thuật toán tham lam, thuật toán nhánh cận, thuật toán qui hoạch động.

# Mô hình thuật toán sinh (Generative Algorithm) 

Mô hình thuật toán sinh được dùng để giải lớp các bài toán liệt kê, bài toán đếm, bài toán tối ưu, bài toán tồn tại thỏa mãn hai điều kiện:

  * **Điều kiện 1:** _Có thể xác định được một thứ tự trên tập các cấu hình cần liệt kê của bài toán. Biết cấu hình đầu tiên, biết cấu hình cuối cùng._

  * **Điều kiện 2:** _Từ một cấu hình chưa phải cuối cùng, ta xây dựng được thuật toán sinh ra cấu hình đứng ngay sau nó._


Mô hình thuật toán sinh được biểu diễn thành hai bước: bước khởi tạo và bước lặp. Tại bước khởi tạo, cấu hình đầu tiên của bài toán sẽ được thiết lập. Điều này bao giờ cũng thực hiện được theo giả thiết của bài toán. Tại bước lặp, quá trình lặp được thực hiện khi gặp phải cấu hình cuối cùng. Điều kiện lặp của bài toán bao giờ cũng tồn tại theo giả thiết của bài toán. Hai chỉ thị cần thực hiện trong thân vòng lặp là đưa ra cấu hình hiện tại và sinh ra cấu hình kế tiếp. Mô hình sinh kế tiếp được thực hiện tùy thuộc vào mỗi bài toán cụ thể. Tổng quát, mô hình thuật toán sinh được thể hiện như dưới đây.

**Thuật toán Generation;**
**begin**
**Bước1 (Khởi tạo):**

_< Thiết lập cấu hình đầu tiên>;_

**Bước 2 (Bước lặp):**

**while** ( _< Lặp khi cấu hình chưa phải cuối cùng>_) **do**

_< Đưa ra cấu hình hiện tại>;_

_< Sinh ra cấu hình kế tiếp>;_ **endwhile** ;

**End**.

**Ví dụ 2.1**. Vector _X_ = ( _x_ 1, _x_ 2, .., _x_ n), trong đó _x_ i = 0, 1 được gọi là một xâu nhị phân có độ dài _n_. Hãy liệt kê các xâu nhị phân có độ dài _n_. Ví dụ với n=4, ta sẽ liệt kê được 24 xâu nhị phân độ dài 4 như trong Bảng 2.1.

**Bảng 2.1**. Các xâu nhị phân độ dài 4


| STT | X=(x1,x2,x3,x4) | STT | X=(x1,x2,x3,x4) |
| --- | --- | --- | --- |
| 0 | 0 0 0 0 | 8 | 1 0 0 0 |
| 1 | 0 0 0 1 | 9 | 1 0 0 1 |
| 2 | 0 0 1 0 | 10 | 1 0 1 0 |
| 3 | 0 0 1 1 | 11 | 1 0 1 1 |
| 4 | 0 1 0 0 | 12 | 1 1 0 0 |
| 5 | 0 1 0 1 | 13 | 1 1 0 1 |
| 6 | 0 1 1 0 | 14 | 1 1 1 0 |
| 7 | 0 1 1 1 | 15 | 1 1 1 1 |

 

**Lời giải:**

**Điều kiện 1** : Gọi thứ tự của xâu nhị phân _X_ =( _x_ 1, _x_ 2,.., _x_ n) là _f_ ( _X_ ). Trong đó, _f_ (X)= _k_ là số chuyển đồi xâu nhị _X_ thành số ở hệ cơ số 10. Ví dụ, xâu _X_ = (1, 0, 1, 1) được chuyển thành số hệ cơ số 10 là 11 thì ta nói xâu _X_ có thứ tự 11. Với cách quan niệm này, xâu đứng sau xâu có thứ tự 11 là 12 chính là xâu đứng ngay sau xâu _X_ = (1, 0, 1, 1). Xâu đầu tiên có thứ tự là _0_ ứng với xâu có _n_ số _0_. Xâu cuối cùng có thứ tự là _2_ n- _1_ ứng với xâu có _n_ số _1_. Như vậy, điều kiện 1 của thuật toán sinh đã được thỏa mãn.

**Điều kiện 2** : Về nguyên tắc ta có thể lấy _k_ = _f_ ( _X_ ) là thứ tự của một xâu bất kỳ theo nguyên tắc ở trên, sau đó lấy thứ tự của xâu kế tiếp là ( _k_ \+ _1_ ) và chuyển đổi ( _k_ + _1_ ) thành số ở hệ cơ số 10 ta sẽ được xâu nhị phân tiếp theo. Xâu cuối cùng sẽ là xâu có n số 1 ứng với thứ tự _k_ = _2_ n- _1._ Với cách làm này, ta có thể coi mỗi xâu nhị phân là một số, mỗi thành phần của xâu là một bít và chỉ cần cài đặt thuật toán chuyển đổi cơ số ở hệ 10 thành số ở hệ nhị phân. Ta có thể xây dựng thuật toán tổng quát hơn bằng cách xem mỗi xâu nhị phân là một mảng các phần tử có giá trị 0 hoặc 1. Sau đó, duyệt từ vị trí bên phải nhất của xâu nếu gặp số 1 ta chuyển thành 0 và gặp số 0 đầu tiên ta chuyển thành 1. Ví dụ với xâu X = (0, 1, 1, 1) được chuyển thành xâu X= (1, 0, 0, 0), xâu X = (1,0,0,0) được chuyển thành xâu X =(1, 0, 0, 1). Lời giải và thuật toán sinh xâu nhị phân kế tiếp được thể hiện trong chương trình dưới đây. Trong đó, thuật toán sinh xâu nhị phân kế tiếp từ một xâu nhị phân bất kỳ là hàm _Next_Bits_String_ ().

#include <iostream>
#include <iomanip> #define MAX 100 using namespace std; int X[MAX], n, dem = 0; // _sử dụng các biến toàn cục X[], n, OK, dem_ bool OK =true; void Init(void){ // _khởi tạo xâu nhị phân đầu tiên_

cout<<"Nhập n="; cin>>n;

for(int i = 1; i<=n; i++) // _thiết lập xâu với n số 0_

X[i]=0;

} void Result(void){ // _đưa ra xâu nhị phân hiện tại_ cout<<"\n Xâu thứ "<<++dem<<":";

for(int i=1; i<=n; i++)

cout<<X[i]<<setw(3);

} void Next_Bits_String(void){ // _thuật toán sinh xâu nhị phân kế tiếp_ int i=n;

while(i>0 && X[i]){ // _duyệt từ vị trí bên phải nhất_

X[i]=0; // _nếu gặp X[i] = 1 ta chuyển thành 0_

i--; // _lùi lại vị trí sau_

}

if (i>0) X[i]=1; // _gặp X[i] =0 đầu tiên ta chuyển thành 1_ else OK = false; // _kết thúc khi gặp xâu có n số 1_
}
int main(void){ // _đây là thuật toán sinh_ Init(); // _thiết lập cấu hình đầu tiên_ while(OK){// _lặp khi chưa phải cấu hình cuối cùng_ Result(); // _đưa ra cấu hình hiện tại_

Next_Bits_String(); // _sinh ra cấu hình kế tiếp_

}

}

**Ví dụ 2.2**. Liệt kê các tập con k phần tử của 1, 2, .., n.

**Lời giải.** Mỗi tập con k phần tử của 1, 2, .., N là một tổ hợp chập K của 1, 2,.., N. Ví dụ với n=5, k= 3 ta sẽ có C(n,k) tập con trong Bảng 2.2.

**Điều kiện 1**. Ta gọi tập con X =( _x_ 1,.. _x_ K) là đứng trước tập con Y =( _y_ 1, _y_ 2,.. _y_ K) nếu tìm được chỉ số t sao cho _x_ 1 = _y_ 1, _x_ 2 = _y_ 2,.., _x_ t-1 = _y_ t-1, _x_ t < _y_ t. Ví dụ tập con _X_ = ( _1, 2, 3_ ) đứng trước tập con _Y_ =( _1, 2, 4_ ) vì ta tìm được t=3 thỏa mãn _x_ 1 = _y_ 1, _x_ 2 = _y_ 2, _x_ 3<y3. Tập con đầu tiên là _X_ = (1 _, 2,.., k_ ), tập con cuối cùng là ( _n–k+1,.., N_ ). Như vậy điều kiện 1 của thuật toán sinh được thỏa mãn.

**Điều kiện 2**. Để ý rằng, tập con cuối cùng (n-k+1,..., n) luôn thỏa mãn đẳng thức X[i] = n – k + i. Ví dụ tập con cuối cùng X[] = (3, 4, 5) ta đều có: X[1] = 3 = 5 – 3 + 1; X[2] = 4 = 5 – 3 + 2; X[3] = 5 = 5 – 3 + 3. Để tìm tập con kế tiếp từ tập con bất kỳ ta chỉ cần duyệt từ phải qua trái tập con X[] = (x1, x2, .., xk) để xác định chỉ số i thỏa mãn điều kiện X[i] n – k + i. Ví dụ với X[] = (1, 4, 5), ta xác định được i=1 vì X[3] = 5 = 5-3+3, X[2] = 4 = 5-3+2, và X[1] = 1 5-3+1. Sau khi xác định được chỉ số i, tập con mới sẽ được sinh là Y[] = (y1,.., yi, ..., yk) ra thỏa mãn điều kiện: y1 = x1, y2 = x2,.., yi-1 = xi-1, yi = xi+1, và yj = xt + j – i với (j = j+1, ..., k).

**Bảng 2.2**. Tập con 3 phần tử của 1, 2, 3, 4, 5


| STT | Tập con |
| --- | --- |
| 1 | 1 2 3 |
| 2 | 1 2 4 |
| 3 | 1 2 5 |
| 4 | 1 3 4 |
| 5 | 1 3 5 |
| 6 | 1 4 5 |
| 7 | 2 3 4 |
| 8 | 2 3 5 |
| 9 | 2 4 5 |
| 10 | 3 4 5 |

 

Chương trình cài đặt thuật toán sinh tập con k phần tử được thể hiện như dưới đây.

Trong đó, thuật toán sinh tổ hợp kế tiếp có tên là Next_Combination().

#include <iostream>
#include <iomanip>  
#define MAX 100  
int X[MAX], n, k, dem=0;  
bool OK = true;  
using namespace std;
void Init(void){ //thiết lập tập con đầu tiên
cout<<"\n Nhập n, k:"; cin>>n>>k;
for(int i=1; i<=k; i++) //tập con đầu tiên là 1, 2, .., k
X[i] = i;

}

void Result(void){ // _đưa ra tập con hiện tại_ cout<<"\n Kết quả "<<++dem<<":";

for(int i=1; i<=k; i++) // _đưa ra_ _X_ [] _=_ ( _x_ 1 _, x_ 2 _, .., x_ k)

cout<<X[i]<<setw(3);

}
void Next_Combination(void){ // _sinh tập con k phần tử từ tập con bất kỳ_

int i = k; // _duyệt từ vị trí bên phải nhất của tập con_ while(i>0 && X[i]== n-k+i) // _tìm i sao cho x i n-k+i_

i--;

if (i>0){// _nếu chưa phải là tập con cuối cùng_

X[i]= X[i]+1; // _thay đổi giá trị tại vị trí i: x i = xi +_1 _;_ for(int j=i+1; j<=k; j++) // _các vị trí j từ i+1,.., k_ X[j] = X[i] + j - i; // được thay đổi là _x j = xi +j - i;_

}

else // _nếu là tập con cuối cùng_

OK = false; / _/ta kết thúc duyệt_
}

int main(void){

Init(); // _khởi tạo cấu hình đầu tiên_

while(OK){ // _lặp trong khi cấu hình chưa phải cuối cùng_ Result(); // _đưa ra cấu hình hiện tại_

Next_Combination(); // _sinh ra cấu hình kế tiếp_

}

}

**Ví dụ 2.3**. Liệt kê các hoán vị của 1, 2, .., n.

**Lời giải.** Mỗi hoán vị của 1, 2, .., N là một cách xếp có tính đến thứ tự của 1, 2,..,N. Số các hoán vị là N!. Ví dụ với N =3 ta có 6 hoán vị dưới đây.

**Bảng 2.3**. Hoán vị của 1, 2, 3.


| STT | Hoán vị |
| --- | --- |
| 1 | 1 2 3 |
| 2 | 1 3 2 |
| 3 | 2 1 3 |
| 4 | 2 3 1 |
| 5 | 3 1 2 |
| 6 | 3 2 1 |

 

**Điều kiện 1.** Có thể xác định được nhiều trật tự khác nhau trên các hoán vị. Tuy nhiên, thứ tự đơn giản nhất có thể được xác định như sau. Hoán vị X =(x1, x2,.., xn) được gọi là đứng sau hoán vị Y = (y1, y2,..,yn) nếu tồn tại chỉ số k sao cho x1 = y1, x2 = y2,…, xk-1 =yk-1, xk<yk. Ví dụ hoán vị X = (1, 2, 3 ) được gọi là đứng sau hoán vị Y =(1, 3, 2) vì tồn tại k =2 để x1 = y1, và x2<y2. Hoán vị đầu tiên là X[] = (1, 2, …, n), hoán vị cuối cùng là X[] = (n, n-1, …, 1).

**Điều kiện 2**. Được thể hiện thông qua hàm Next_Permutation() như chương trình dưới đây.

#include <iostream>
#include <iomanip> #define MAX 100 int X[MAX], n, dem=0; bool OK = true; using namespace std; void Init(void){ // _thiết lập hoán vị đầu tiên_ cout<<"\n Nhap n:"; cin>>n;

for(int i=1; i<=n; i++) // _thiết lập X_ [] _=_ ( _1, 2, ..,n_ )

X[i] = i;

} void Result(void){ // _đưa ra hoán vị hiện tại_ cout<<"\n Kết quả "<<++dem<<":";

for(int i=1; i<=n; i++)

cout<<X[i]<<setw(3);

}
void Next_Permutation(void){ // _sinh ra hoán vị kế tiếp_ int j = n-1; // _xuất phát từ vị trí j = n-1_
while(j>0 && X[j]>X[j+1]) // _tìm chỉ số j sao cho X[j] < X[j+1]_ j--;
if ( j > 0){ // _nếu chưa phải hoán vị cuối cùng_ int k = n; // _xuất phát từ vị trí k = n_

while(X[j]>X[k]) // _tìm chỉ số k sao cho X[j] < X[k]_

k--;

int t = X[j]; X[j] = X[k]; X[k]=t; // _đổi chỗ X[j] cho X[k]_ int r = j+1, s = n; while (r<=s){ // _lật ngược lại đoạn từ j+1,..,n_ t=X[r]; X[r]=X[s]; X[s]=t;

r++; s--;

}

}

else // _nếu là cấu hình cuối cùng_

OK = false; // _ta kết thúc duyệt_
}
int main(void){ // _đây là thuật toán sinh_ Init(); // _thiết lập cấu hình đầu tiên_
while(OK){ // _lặp trong khi cấu hình chưa phải cuối cùng_ Result(); // _đưa ra cấu hình hiện tại_

Next_Permutation(); // _sinh ra cấu hình kế tiếp_

}

}

# Mô hình thuật toán đệ qui (Recursion Algorithm) 

Một đối tượng được định nghĩa trực tiếp hoặc gián tiếp thông qua chính nó được gọi là phép định nghĩa bằng đệ qui. Thuật toán giải bài toán _P_ một cách trực tiếp hoặc gián tiếp thông qua bài toán _P_ ’ giống như _P_ được gọi là thuật toán đệ qui giải bài toán _P_. Một hàm được gọi là đệ qui nếu nó được gọi trực tiếp hoặc gián tiếp đến chính nó.

Tổng quát, một bài toán có thể giải được bằng đệ qui nếu nó thỏa mãn hai điều kiện:

  * **Phân tích được** _: Có thể giải được bài toán P bằng bài toán P’ giống như P. Bài tóa P’ và chỉ khác P ở dữ liệu đầu vào. Việc giải bài toán P’ cũng được thực hiện theo cách phân tích giống như P._

  * **Điều kiện dừng** _: Dãy các bài toán P’ giống như P là hữu hạn và sẽ dừng tại một bài toán xác định nào đó._


Thuật toán đệ qui tổng quát có thể được mô tả như sau:

_Thuật toán Recursion ( P )_ {

  1. _Nếu P thỏa mãn điều kiện dừng:_


< _Giải P với điều kiện dừng_ >;

  2. Nếu _P_ không thỏa mãn điều kiện dừng:


_< Giải P’ giống như P:Recursion(P’)>;_

}

**Ví dụ 2.4**. Tìm tổng của n số tự nhiên đầu tiên bằng phương pháp đệ qui.

**Lời giải**. Gọi Sn là tổng của n số tự nhiên. Khi đó:

  * **Bước phân tích** : dễ dàng phận thấy tổng n số tự nhiên Sn = n + Sn-1, với n1. • **Điều kiện dừng** : S0 = 0 nếu n = 0;


Từ đó ta có lời giải của bài toán như sau:

int Tong (int n ) {

if (n ==0 ) return(0); // _Điều kiện dừng_

else return(n + Tong(n-1)); // _Điều kiện phân tích được_

}

Chẳng hạn ta cần tìm tổng của 5 số tự nhiên đầu tiên, khi đó:

S = Tong(5)

= 5 + Tong(4)

= 5 + 4 + Tong(3)

= 5 + 4 + 3 + Tong(2)

= 5 + 4 + 3 + 2+ Tong(1)

= 5 + 4 + 3 + 2 + 1 + Tong(0)

= 5 + 4 + 3 + 2 + 1 + 0

= 15

**Ví dụ 2.5**. Tìm n!.

**Lời giải**. Gọi Sn là n!. Khi đó:

  * **Bước phân tích** : Sn = n*(n-1)! nếu n>0;

  * **Điều kiện dừng** : s0=1 nếu n=0.


Từ đó ta có lời giải của bài toán như sau:
long Giaithua (int n ) {

if (n ==0 ) return(1); // _Điều kiện dừng_

else return(n *Giaithua(n-1)); // _Điều kiện phân tích được_

} **Ví dụ 2.6.** Tìm ước số chung lớn nhất của a và b bằng phương pháp đệ qui.

**Lời giải**. Gọi d =USCLN(a,b). Khi đó:

  * **Bước phân tích** : nếu b0 thì d = USCLN(a, b) = USCLN(b, r), trong đó a =b, b = r = a mod b .

  * **Điều kiện dừng** : nếu b = 0 thì a là ước số chung lớn nhất của a và b. Từ đó ta có lời giải của bài toán như sau: int USCLN (int a, int b ) { if (a ==b ) return(a); // _Điều kiện dừng_ else { // _Điều kiện phân tích được_ int r = a % b; a = b; b = r; return(USCLN(a, b)); // _giải bài toán USCLN(a, b)_


}

}