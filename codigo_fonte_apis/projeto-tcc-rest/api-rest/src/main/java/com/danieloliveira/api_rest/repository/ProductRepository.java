package com.danieloliveira.api_rest.repository;


import com.danieloliveira.api_rest.model.Product;
import org.springframework.stereotype.Repository;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

@Repository
public class ProductRepository {

    private final Map<Long, Product> dataBase = new ConcurrentHashMap<>();
    private final AtomicLong sequence = new AtomicLong(1);

    public Product findById(long id) {
        return dataBase.get(id);
    }

    public void save(Product product) {
        if (product.getId() == null) {
            product.setId(sequence.getAndIncrement());
        }
        dataBase.put(product.getId(), product);
    }

    public void delete(long id) {
        dataBase.remove(id);
    }

    public Long incrementSequence(){
        return this.sequence.incrementAndGet();
    }
}
