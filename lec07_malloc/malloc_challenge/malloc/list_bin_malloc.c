//
// >>>> malloc challenge! <<<<
//
// Your task is to improve utilization and speed of the following malloc
// implementation.
// Initial implementation is the same as the one implemented in simple_malloc.c.
// For the detailed explanation, please refer to simple_malloc.c.

#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

//
// Interfaces to get memory pages from OS
//

void *mmap_from_system(size_t size);
void munmap_to_system(void *ptr, size_t size);

//
// Struct definitions
//

 #define BIN_COUNT 6  

int get_bin_index(size_t size) {
  if(size < 128) return 0;
  if(size == 128) return 1;
  if(size <= 256) return 2;
  if(size <= 512) return 3;
  if(size <= 1024) return 4;
  return 5;
}

typedef struct my_metadata_t {
  size_t size;
  struct my_metadata_t *next;
} my_metadata_t;

typedef struct my_heap_t {
  my_metadata_t *free_head[BIN_COUNT];
  my_metadata_t dummy[BIN_COUNT];
} my_heap_t;

//
// Static variables (DO NOT ADD ANOTHER STATIC VARIABLES!)
//
my_heap_t my_heap;

//
// Helper functions (feel free to add/remove/edit!)
//

void my_remove_from_free_list(my_metadata_t *metadata, my_metadata_t *prev, int bin);

// metadata_cur 現在の空き領域
// metadata これから空き領域にしようとしている場所
void my_add_to_free_list(my_metadata_t *metadata) {

 for (int bin = 0; bin < BIN_COUNT; bin++) {
   my_metadata_t *metadata_cur = my_heap.free_head[bin];
   my_metadata_t *metadata_prev = NULL;
   while(metadata_cur){

    // 左の領域がfreeなら結合する
    if((char*) metadata_cur + sizeof(my_metadata_t) + metadata_cur->size == (char *)metadata){
      metadata_cur->size += sizeof(my_metadata_t) + metadata->size;
      return;
    }

    // 右の領域がfreeなら結合する
    if((char*) metadata + sizeof(my_metadata_t) + metadata->size == (char*) metadata_cur){
        metadata->size += sizeof(my_metadata_t) + metadata_cur->size;
        my_remove_from_free_list(metadata_cur,metadata_prev,bin);
        // 結合したのでreturnで終了（二重登録を防ぐ）
        metadata->next = NULL;
        int bin_index = get_bin_index(metadata->size);
        metadata->next = my_heap.free_head[bin_index];
        my_heap.free_head[bin_index] = metadata;
        return;
    }

    metadata_prev = metadata_cur;
    metadata_cur = metadata_cur->next;
   }
  }

   // 結合しなかった場合のみfree listに登録
   metadata->next = NULL;
   int bin_index = get_bin_index(metadata->size);
   metadata->next = my_heap.free_head[bin_index];
   my_heap.free_head[bin_index] = metadata;
  }

void my_remove_from_free_list(my_metadata_t *metadata, my_metadata_t *prev,int bin) {
  if (prev) {
    prev->next = metadata->next;
  } else {
    my_heap.free_head[bin] = metadata->next;
  }
  metadata->next = NULL;
}

//
// Interfaces of malloc (DO NOT RENAME FOLLOWING FUNCTIONS!)
//

// This is called at the beginning of each challenge.
void my_initialize() {
  for (int i = 0; i < BIN_COUNT; i++) {
    my_heap.free_head[i] = &my_heap.dummy[i];
    my_heap.dummy[i].size = 0;
    my_heap.dummy[i].next = NULL;
  }
}



// my_malloc() is called every time an object is allocated.
// |size| is guaranteed to be a multiple of 8 bytes and meets 8 <= |size| <=
// 4000. You are not allowed to use any library functions other than
// mmap_from_system() / munmap_to_system().
void *my_malloc(size_t size) {
  // ヒストグラム用ログ出力
  FILE *fp = fopen("size_log.txt", "a");
  if (fp) {
    fprintf(fp, "%zu\n", size);
    fclose(fp);
  }

  int start_bin = get_bin_index(size);
  int best_fit_bin = -1;  
  my_metadata_t *best_fit_metadata = NULL;
  my_metadata_t *best_fit_metadata_prev = NULL;

  // First-fit: Find the first free slot the object fits.
  // TODO: Update this logic to Best-fit!
  // 空き領域に置ける領域の中で一番小さいものを見つける
    
  for (int bin = start_bin; bin < BIN_COUNT; bin++) {
    my_metadata_t *metadata = my_heap.free_head[bin];
    my_metadata_t *metadata_prev = NULL;

    while (metadata) {
      if(metadata->size >= size){
        if(!best_fit_metadata || metadata->size < best_fit_metadata->size){
          best_fit_metadata = metadata;
          best_fit_metadata_prev = metadata_prev;
          best_fit_bin = bin;
        }
      }
      metadata_prev = metadata;
      metadata = metadata->next;
    }
  }

  // now, metadata points to the first free slot
  // and prev is the previous entry.

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
    my_metadata_t *metadata = (my_metadata_t *)mmap_from_system(buffer_size);
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
  my_remove_from_free_list(best_fit_metadata, best_fit_metadata_prev,best_fit_bin);

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

// This is called every time an object is freed.  You are not allowed to
// use any library functions other than mmap_from_system / munmap_to_system.
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
