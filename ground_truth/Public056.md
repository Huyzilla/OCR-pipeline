# Public_056

Như đã trình bày trong Chương 1, một kiểu dữ liệu trừu tượng (ADTs) được xác định khi ta xây dựng đầy đủ hai phần: cấu trúc dữ liệu cùng các phép toán trên cấu trúc dữ liệu đó. Nội dung của chương này trình bày ba kiểu dữ liệu trừu tượng quan trọng đó là danh sách liên kết, ngăn xếp và hàng đợi. Mỗi kiểu dữ liệu trừu tượng được xây dựng giải quyết lớp các vấn đề cụ thể của khoa học máy tính. Đối với người học, mỗi cấu trúc dữ liệu trừu tượng cần làm chủ được bốn điểm quan trọng sau:

  * Định nghĩa cấu trúc dữ liệu ADTs.

  * Biểu diễn cấu trúc dữ liệu ADTs.

  * Thao tác (phép toán) trên cấu trúc dữ liệu ADTs.

  * Ứng dụng của cấu trúc dữ liệu ADTs.


# Danh sách liên kết đơn (Single Linked List)

Như ta đã biết mảng ( _array_ ) là tập có thứ tự các phần tử có cùng chung một kiểu dữ liệu và được tổ chức liên tục nhau trong bộ nhớ. Ưu điểm lớn nhất của mảng là đơn giản và xử lý nhanh nhờ cơ chế truy cập phần tử trực tiếp vào các phần tử của mảng. Hạn chế lớn nhất của mảng là số lượng phần tử không thay đổi gây nên hiện tượng thừa bộ nhớ trong một số trường hợp và thiếu bộ nhớ trong một số trường hợp khác. Đối với một số bài toán có dữ liệu lớn, nhiều khi ta không đủ không gian nhớ tự do liên tục để cấp phát cho mảng. Để khắc phục hạn chế này ta có thể xây dựng kiểu dữ liệu danh sách liên kết đơn được định nghĩa, biểu diễn và thao tác như dưới đây.

## Định nghĩa danh sách liên kết đơn

Tập hợp các node thông tin được tổ chức rời rạc trong bộ nhớ. Trong đó, mỗi node gồm có hai thành phần:

  * Thành phần dữ liệu ( _data_ ): dùng để lưu trữ thông tin của node.

  * Thành phần con trỏ ( _pointer_ ): dùng để liên kết với node dữ liệu tiếp theo.


## Biểu diễn danh sách liên kết đơn

Để biểu diễn danh sách liên kết đơn ta sử dụng phương pháp định nghĩa cấu trúc tự trỏ của các ngôn ngữ lập trình. Giả sử thành phần thông tin của mỗi node được định nghĩa như một cấu trúc Item như sau:

struct Item {
<Kiểu 1> <Thành viên 1>;
<Kiểu 2> <Thành viên 2>;
……………………………;
<Kiểu N> <Thành viên N>;
};
Khi đó, danh sách liên kết đơn được định nghĩa như sau: struct node {
Item infor; // _Thành phần thông tin của node;_
struct node *next; // _thành phần con trỏ của node_
} *Start; // _Start là một danh sách liên kết đơn_

![](images/image1.png)

**Hình 3.1. Biểu diễn danh sách liên kết đơn**

## Thao tác trên danh sách liên kết đơn

Các thao tác trên danh sách liên kết đơn bao gồm:

  * Tạo node rời rạc có giá trị value cho danh sách liên kết đơn

  * Thêm một node vào đầu danh sách liên kết đơn.

  * Thêm một node vào cuối danh sách liên kết đơn.

  * Thêm node vào vị trí xác định trong danh sách liên kết đơn.

  * Loại node trong sách liên kết đơn.

  * Tìm node trong sách liên kết đơn.

  * Sắp xếp node trong danh sách liên kết đơn.

  * Sửa đổi nội dung node trong sách liên kết đơn.

  * Đảo ngược các node trong danh sách liên kết đơn.

  * Duyệt các node của danh sách liên kết đơn.


Để đơn giản, ta xem thành phần thông tin của node (Item) là một số nguyên. Khi đó, các thao tác trên danh sách liên kết đơn ta định nghĩa một lớp các thao tác như sau:

struct node { // _biểu diễn node_
int info; // _thành phần thông tin của node_
struct node *next; // _thành phần con trỏ của node_
}*start; // _danh sách liên kết đơn: *start._
class single_linked_list { // _biểu diễn lớp danh sách liên kết đơn_
public:
node* create_node(int);// _Tạo một node cho danh sách liên kết đơn_
void insert_begin(); // _thêm node vào đầu DSLKĐ_
void insert_pos(); // _thêm node tại vị trí cụ thể trên DSLKĐ_
void insert_last(); // _thêm node vào cuối DSLKĐ_
void delete_pos(); // _loại node tại vị trí cho trước trên DSLKĐ_
void sort(); // _sắp xếp nội dung các node theo thứ tự tăng dần_
void search(); // _tìm kiếm node trên DSLKĐ_
void update(); // _sửa đổi thông tin của node trên DSLKĐ_
void reverse(); // _đảo ngược danh sách liên kết đơn_
void display(); // _hiển thị nội dung DSLKĐ_
single_linked_list(){// _constructor của lớp single linked list_. start = NULL;// _chú ý start là biến toàn cục_
}
};

**Thao tác:** _tạo một node rời rạc có giá trị value cho DSLKĐ_ **.**

node *single_linked_list::create_node(int value){
struct node *temp; // _khai báo hai con trỏ node *temp_ temp = new(struct node); // _cấp phát miền nhớ cho temp_ if (temp == NULL){ // _nếu không đủ không gian nhớ_
cout<<“ _không đủ bộ nhớ để cấp phát_ "<<endl; return 0;
else {
temp->info = value;// _thiết lập thông tin cho node temp_
temp->next = NULL; // _thiết lập liên kết cho node temp_
return temp;// _trả lại node temp đã được thiết lập_
}

}

**Thao tác: _thêm node vào đầu DSLKĐ_.**

void single_linked_list::insert_begin(){ // _chèn node vào đầu DSLKĐ_
int value; cout<<“Nhập giá trị node:"; cin>>value; // _giá trị node cần chèn_
struct node *temp, *p; // _sử dụng hai con trỏ temp và p_
temp = create_node(value);// _tạo một node rời rạc có giá trị value_
if (start == NULL){ // _nếu danh sách liên kết rỗng_
start = temp; // _danh sách liên kết chính là node temp_
start->next = NULL; // _không có liêt kết với node khác_
}
else { // _nếu danh sách không rỗng_
p = start; // _p trỏ đến node đầu của start_
start = temp; // _node temp trở thành node đầu tiên của start_
start->next = p;// _các node còn lại chính là p_
}
}

Hình 3.2. dưới đây mô tả phép thêm node vào đầu danh sách liên kết đơn.

![](images/image2.png)

**Hình 3.2. Thêm node vào đầu danh sách liên kết đơn**

**Thao tác thêm node vào cuối danh sách liên kết đơn** :

void single_linked_list::insert_last() **{** // _thêm node vào cuối DSLKĐ_

int value;
cout<<“Nhập giá trị cho node: ";cin>>value; // _nhập giá trị node_
struct node *temp, *s; // _sử dung hai con trỏ temp và s_
temp = create_node(value);// _tạo node rời rạc có giá trị value_
if(start==NULL) {// _trường hợp DSLKĐ rỗng_
start = temp;
temp->next=NULL;
}
s = start; // _s trỏ đến node đầu danh sách_
while (s->next != NULL){ // _di chuyển s đến node cuối cùng_
s = s->next;
}
temp->next = NULL; // _temp không chỏ đi đâu nữa_ s->next = temp; // _thiết lập liên kết cho s_ cout<<“ _Hoàn thành thêm node vào cuối_ "<<endl;

}

![](images/image3.png)

**Hình 3.3. Thêm node vào cuối danh sách liên kết đơn**

**Thao tác thêm node vào vị trí pos của danh sách liên kết đơn** :

void single_linked_list::insert_pos() **{** // _thêm node vào vị trí pos_

int value, pos, counter = 0; cout<<"Nhap gia tri node:";cin>>value; struct node *temp, *s, *ptr; // _sử dụng ba con trỏ node_
temp = create_node(value);// _tạo node rời rạc có giá trị value_
cout<<“Nhập vị trí node cần thêm: ";cin>>pos; int i; s = start; // _s trỏ đến node đầu tiên_
while (s != NULL){ // _đếm số node của DSLKĐ_
s = s->next; counter++;

}

if (counter==0) {// _trường hợp DSLK đơn rỗng_
cout<<”Danh sách rỗng”; return;
}
if (pos == 1){ // _nếu pos là vị trí đầu tiên_

if (start == NULL){ // _trường hợp DSLKĐ rỗng_

start = temp; start->next = NULL;

}
else { // _thêm node temp vào đầu DSLKĐ_
ptr = start; start = temp; start->next = ptr;
}
}
else if (pos > 1 && pos <= counter){ // _trường hợp pos hợp lệ_
s = start; // _s trỏ đến node đầu tiên_
for (i = 1; i < pos; i++){ // _di chuyển đến node pos-1_
ptr = s; s = s->next;
}
ptr->next = temp; temp->next = s; // _thiết lập liên kết cho node_
}
else { cout<<“ _Vượt quá giới hạn DSLKĐ_ "<<endl; }

}

![](images/image4.png)

**Hình 3.4. Thêm node vào vị trí pos**

**Thao tác loại node tại vị trí pos** :

void single_linked_list::delete_pos() **{** // _loại node ở vị trí pos_

int pos, i, counter = 0;
if (start == NULL){ // _nếu danh sách liê kết đơn rỗng_
cout<<“Không thực hiện được"<<endl; return;
}
cout<<“ _Vị trí cần loại bỏ_ :";cin>>pos;
struct node *s, *ptr; s = start; // _s trỏ đến đầu danh sách_
if (pos == 1){// _nếu vị trí loại bỏ là node đầu tiên_
start = s->next; s->next=NULL; free(s);}
else {
while (s != NULL) { // _đếm số node của DSLKĐ_
s = s->next; counter++;}
if (pos > 0 && pos <= counter){ // _nếu vị trí pos hợp lệ_
s = start;// _s trỏ đến node đầu của danh sách_
for (i = 1;i < pos; i++){ // _di chuyển đến vị trí pos-1_
ptr = s; s = s->next;
}
ptr->next = s->next; // _thiết lập liên kết cho node_
}
else { cout<<"Vi tri ngoai danh sach"<<endl; } free(s); // _giải phóng s_
cout<<"Node da bi loai bo"<<endl;
}

}

![](images/image5.png)

**Hình 3.5. Thao tác loại node ở vị trí pos**

**Thao tác sửa đổi nội dung của node** :

void single_linked_list::update() **{** // _sửa đổi thông tin của node_

int value, pos, i;
if (start == NULL){ // _nếu danh sách LKĐ rỗng_
cout<<“ _Không thực hiện được_ "<<endl; return;
}
cout<<“Nhập vị trí node cần sửa:";cin>>pos; cout<<“ _Giá trị mới của node_ :";cin>>value; struct node *s, *ptr; // _sử dụng hai con trỏ s và ptr_ s = start; // _s trỏ đến node đầu tiên_
if (pos == 1) { start->info = value;} // _sửa luôn node đầu tiên_
else { // _nếu pos không phải là node đầu tiên_
for (i = 0;i < pos - 1;i++){// _chuyển s đến vị trí pos-1_
if (s == NULL){// _Nếu s là node cuối cùng_
cout<<"Vị trí "<<pos<<" _không hợp lệ_ “; return;
}
s = s->next;
}
s->info = value; // _Sửa đổi thông tin cho node_
}
cout<<“ _Hoàn thành việc sửa đổi_ "<<endl;

}

**Thao tác duyệt danh sách liên kết đơn** :

void single_linked_list::display() **{** // _hiển thị nội dung DSLKĐ_

struct node *temp; // _sử dụng một con trỏ temp_
if (start == NULL){ // _nếu danh sách rỗng_ cout<<“ _Có gì đâu mà hiển thị_ "<<endl; return;
}
temp = start; // _temp trỏ đến node đầu trong DSLKĐ_
cout<<“ _Nội dung DSLKĐ_ : "<<endl;
while (temp != NULL) { // _lặp cho đến node cuối cùng_ cout<<temp->info<<"->"; // _hiển thị thông tin node_ temp = temp->next; // _di chuyển đến node tiếp theo_
}
cout<<" _NULL_ "<<endl; // _node cuối cùng là NULL_

}

**Thao tác tìm node trong danh sách liên kết đơn** :

_**void single_linked_list::search(){**_ // _Tìm kiếm node_

int value, pos = 0; bool flag = false;
if (start == NULL){// _nếu danh sách rỗng_ cout<<“ _ta không có gì để tìm_ "<<endl; return;
}
cout<<“ _Nội dung node cần tìm_ :";cin>>value; struct node *s; s = start;// _s trỏ đến đầu danh sách_ while (s != NULL){ pos++;
if (s->info == value){// _Nếu s- >infor là value_
flag = true;
cout<<“ _Tìm thấy_ "<<value<<" _tại vị trí_ "<<pos<<endl;
}
s = s->next;
}
if (!flag) {// _đến cuối vẫn không thấy_
cout<<“ _Giá trị_ "<<value<<“ _không tồn tại_ "<<endl;
}

}

**Thao tác sắp xếp các node trong danh sách liên kết đơn** : void single_linked_list::sort() **{** // _sắp xếp theo nội dung các node_

struct node *ptr, *s; // _sử dụng hai con trỏ ptr và s_
int value; // _giá trị trung gian_
if (start == NULL){// _nếu danh sách rỗng_ cout<<“ _không có gì để sắp xếp_ "<<endl; return;
}
ptr = start;// _ptr trỏ đến node đầu danh sách_
while (ptr != NULL){ // _lặp trong khi ptr khác rỗng_
for (s = ptr->next; s !=NULL; s = s->next){ // _s là node tiếp theo_
if (ptr->info > s->info){// _nếu điều này xảy ra_
value = ptr->info;// _tráo đổi nội dung hai node_
ptr->info = s->info; s->info = value;
}
}
ptr = ptr->next;
}

}

**Thao tác đảo ngược các node của DSLKĐ** :

void single_linked_list::reverse() **{** // _đảo ngược danh sách_

struct node *ptr1, *ptr2, *ptr3; // _sử dụng ba con trỏ node_
if (start == NULL) {// _Nếu danh sách rỗng_
cout<<“ _ta không cần đảo_ "<<endl; return;
}
if (start->next == NULL){//Nếu danh sách chỉ có một node cout<<“ _đảo ngược là chính nó_ "<<endl; return;
}
ptr1 = start; // _ptr1 trỏ đến node đầu tiên_
ptr2 = ptr1->next;// _ptr2 trỏ đến node kế tiếp của ptr1_ ptr3 = ptr2->next;// _ptr3 trỏ đến nod kế tiếp của ptr2_ ptr1->next = NULL;// _Ngắt liên kết ptr1_
ptr2->next = ptr1;// _node ptr2 bây giờ đứng trước node ptr1_
while (ptr3 != NULL){// _Lặp nếu ptr3 khác rỗng_ ptr1 = ptr2; // _ptr1 lại bắt đầu tại vị trí ptr2_ ptr2 = ptr3; // _ptr2 bắt đầu tại vị trí ptr3_
ptr3 = ptr3->next; // _ptr3 trỏ đến node kế tiếp_
ptr2->next = ptr1; // _Thiết lập liên kết cho ptr2_
}
start = ptr2; // _node đầu tiên bây giờ là ptr2_

}

**//Chương trình cài đặt các thao tác trên danh sách liên kết đơn:**

#include<iostream> using namespace std;

struct node { // _biểu diễn danh sách liên kết đơn_

int info; // _thành phần thông tin_
struct node *next; // _thành phần liên kết_

}*start;

class single_linked_list { // _biểu diễn lớp single_linked_list_

public:
node* create_node(int);// _tạo node rời rạc có giá trị value_
void insert_begin();// _thêm node vào đầu danh sách liên kết đơn_
void insert_pos();// _thêm node vào vị trí pos trong danh sách liên kết đơn_
void insert_last();// _thêm node vào cuối danh sách liên kết đơn_ void delete_pos();// _loại node tại vị trí pos của sách liên kết đơn_ void sort();// _sắp xếp theo giá trị node cho danh sách liên kết đơn_ void search();// _tìm node trong danh sách liên kết đơn_
void update(); // _cập nhật thông tin cho node_
void reverse(); // _đảo ngược các node trong danh sách liên kết đơn_ void display(); // _duyệt danh sách liên kết đơn_ single_linked_list(){// _constructor của lớp_
start = NULL;
}

};