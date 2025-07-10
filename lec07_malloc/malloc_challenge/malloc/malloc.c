#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/time.h>

void *mmap_from_system(size_t size);
void munmap_to_system(void *ptr, size_t size);

// Each object or free slot has metadata just prior to it:
//
// ... | m | object | m | free slot | m | free slot | m | object | ...
//
// where |m| indicates metadata. The metadata is needed for two purposes:
//
// 1) For an allocated object:
//   *  |size| indicates the size of the object. |size| does not include
//      the size of the metadata.
//   *  |next| is unused and set to NULL.
// 2) For a free slot:
//   *  |size| indicates the size of the free slot. |size| does not include
//      the size of the metadata.
//   *  The free slots are linked with a singly linked list (we call this a
//      free list). |next| points to the next free slot.
typedef struct my_metadata_t {
  size_t size;
  struct my_metadata_t *next;
} my_metadata_t;

// The global information of the my malloc.
//   *  |free_head| points to the first free slot.
//   *  |dummy| is a dummy free slot (only used to make the free list
//      implementation myr).
typedef struct my_heap_t {
  my_metadata_t *free_head;
  my_metadata_t dummy;
} my_heap_t;

my_heap_t my_heap;

// Remove a free slot from the free list.
void my_remove_from_free_list(my_metadata_t *metadata,
                                  my_metadata_t *prev) {
  if (prev) {
    prev->next = metadata->next;
  } else {
    my_heap.free_head = metadata->next;
  }
  metadata->next = NULL;
}

// Add a free slot to the beginning of the free list.
void my_add_to_free_list(my_metadata_t *metadata) {
  my_metadata_t *current = my_heap.free_head; //空き領域　(free listの先頭)
  my_metadata_t *prev = NULL;
  int merged = 0;
  
  while(current){
    my_metadata_t *next = current->next; // 先に次のポインタを保存
    
    //左結合： freeにしようとしてるmetadataの前(左)が空き領域だった時
    if ((char*)current + sizeof(my_metadata_t) + current->size == (char*)metadata){
        my_remove_from_free_list(current, prev);
        current->size += sizeof(my_metadata_t) + metadata->size;
        metadata = current; 
        merged = 1;
        break; 
    }
    //右結合：freeにしようとしてるmetadataの次が空き領域だったとき
    // metadataのポインタの位置は変わらない
    else if((char*)metadata + sizeof(my_metadata_t) + metadata->size == (char*)current){
        my_remove_from_free_list(current, prev);
        metadata->size += sizeof(my_metadata_t) + current->size;
        merged = 1;
        break; 
    }
    
    prev = current;
    current = next;
  }

    metadata->next = my_heap.free_head;
    my_heap.free_head = metadata;
  }




// This is called at the beginning of each challenge.
void my_initialize() {
  my_heap.free_head = &my_heap.dummy;
  my_heap.dummy.size = 0;
  my_heap.dummy.next = NULL;
}

// This is called every time an object is allocated. |size| is guaranteed
// to be a multiple of 8 bytes and meets 8 <= |size| <= 4000. You are not
// allowed to use any library functions other than mmap_from_system /
// munmap_to_system.
void *my_malloc(size_t size) {
  my_metadata_t *metadata = my_heap.free_head; //空き領域
  my_metadata_t *prev = NULL;

  // best fit
  my_metadata_t *best_fit_metadata = NULL;
  my_metadata_t *best_fit_prev = NULL;


  while (metadata) {
    if(metadata->size >= size){
    if(!best_fit_metadata || best_fit_metadata->size > metadata->size){
        best_fit_metadata = metadata;
        best_fit_prev = prev;
        // ちょうど大きさが一致してたらbreak
        if(best_fit_metadata->size == size){
          break;
        }
    }
    }
    prev = metadata;
    metadata = metadata->next;
  }

  if (!best_fit_metadata) {
    // There was no free slot available. We need to request a new memory region
    // from the system by calling mmap_from_system().
    //
    //     | metadata | free slot |
    //     ^
    //     metadata
    //     <---------------------->
    //            buffer_size
    size_t buffer_size = 4096;
    my_metadata_t *metadata =
        (my_metadata_t *)mmap_from_system(buffer_size);
    metadata->size = buffer_size - sizeof(my_metadata_t);
    metadata->next = NULL;
    // Add the memory region to the free list.
    my_add_to_free_list(metadata);
    // Now, try my_malloc() again. This should succeed.
    return my_malloc(size);
  }

  // |ptr| is the beginning of the allocated object.
  //
  // ... | metadata | object | ...
  //     ^          ^
  //     metadata   ptr
  void *ptr = best_fit_metadata + 1;
  size_t remaining_size = best_fit_metadata->size - size;
  // Remove the free slot from the free list.
  my_remove_from_free_list(best_fit_metadata, best_fit_prev);

  if (remaining_size > sizeof(my_metadata_t)) {
    // Shrink the metadata for the allocated object
    // to separate the rest of the region corresponding to remaining_size.
    // If the remaining_size is not large enough to make a new metadata,
    // this code path will not be taken and the region will be managed
    // as a part of the allocated object.
    best_fit_metadata->size = size;
    // Create a new metadata for the remaining free slot.
    //
    // ... | metadata | object | metadata | free slot | ...
    //     ^          ^        ^
    //     metadata   ptr      new_metadata
    //                 <------><---------------------->
    //                   size       remaining size
    my_metadata_t *new_metadata = (my_metadata_t *)((char *)ptr + size);
    new_metadata->size = remaining_size - sizeof(my_metadata_t);
    new_metadata->next = NULL;
    // Add the remaining free slot to the free list.
    my_add_to_free_list(new_metadata);
  }
  return ptr;
}

// This is called every time an object is freed.  You are not allowed to use
// any library functions other than mmap_from_system / munmap_to_system.
void my_free(void *ptr) {
  // Look up the metadata. The metadata is placed just prior to the object.
  //
  // ... | metadata | object | ...
  //     ^          ^
  //     metadata   ptr
  my_metadata_t *metadata = (my_metadata_t *)ptr - 1;
  // Add the free slot to the free list.
  my_add_to_free_list(metadata);
}

// This is called at the end of each challenge.
void my_finalize() {
  // Nothing is here for now.
  // feel free to add something if you want!
}

void test() {
  // Implement here!
  assert(1 == 1); /* 1 is 1. That's always true! (You can remove this.) */
}